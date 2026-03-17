import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-ue-client-tx-id",
};

const EVENT_JSON_FORMAT = `{
  "title": "event name",
  "start_time": "ISO8601 datetime (YYYY-MM-DDTHH:MM:SS)",
  "end_time": "ISO8601 datetime or null",
  "location": "venue/address or null",
  "description": "brief description or null",
  "url": "website if visible or null"
}`;

function getSharedRules(): string {
  const today = new Date().toISOString().substring(0, 10);
  return `Rules:
- Today's date is ${today}. Use this to calculate upcoming dates (e.g., "next Tuesday" means the next Tuesday on or after today).
- If you cannot determine the exact time, make a reasonable guess (e.g., evening events at 19:00).
- If end_time is unknown, estimate a reasonable duration (e.g., 1 hour for meetups, 2-3 hours for concerts/festivals).
- If the date/time is completely unreadable, set start_time to null.
- Keep description brief (1-2 sentences max).
- Return ONLY the JSON object, no markdown or explanation.`;
}

function getImageExtractionPrompt(): string {
  return `Extract event details from this poster image. Return ONLY valid JSON, no other text:
${EVENT_JSON_FORMAT}

${getSharedRules()}`;
}

function getAudioExtractionPrompt(): string {
  return `Extract event details from this transcript of an audio recording (e.g., a voice memo, radio ad, or voicemail about an event). Return ONLY valid JSON, no other text:
${EVENT_JSON_FORMAT}

${getSharedRules()}
- The transcript may contain filler words, false starts, or informal speech — extract the key event details.
- If multiple events are mentioned, extract only the first/primary one.
- If a day of the week is mentioned or implied (e.g., "Thursday night trivia", "Saturday morning farmers market"), set start_time to the NEXT upcoming occurrence of that day.
- If the event sounds recurring (e.g., "every week", "weekly", a named day implying regularity), mention the recurrence in the description (e.g., "Weekly on Thursdays").
- If the speaker mentions where to find more info (e.g., "check meetup for details", "it's on eventbrite", "search Facebook for downtown art walk"), construct a plausible search URL for the url field:
  - Facebook: https://www.facebook.com/search/top/?q={event+name+city}
  - Meetup: https://www.meetup.com/find/?keywords={event+name}&location={city}
  - Eventbrite: https://www.eventbrite.com/d/{state}--{city}/{event-name}
  - Generic: https://www.google.com/search?q={event+name+city}
- If no source is mentioned, leave url as null.`;
}

function getTextExtractionPrompt(): string {
  return `Extract event details from the following text (e.g., copied from a website, email, flyer, or social media post). Return ONLY valid JSON, no other text:
${EVENT_JSON_FORMAT}

${getSharedRules()}
- The text may contain formatting artifacts, extra whitespace, or surrounding context — focus on extracting the core event details.
- If multiple events are mentioned, extract only the first/primary one.
- If a day of the week is mentioned (e.g., "this Thursday", "every Saturday"), set start_time to the NEXT upcoming occurrence of that day.
- If the event sounds recurring (e.g., "every week", "weekly", a named day implying regularity), mention the recurrence in the description (e.g., "Weekly on Thursdays").`;
}

function parseEventJson(text: string): any {
  try {
    return JSON.parse(text);
  } catch (e) {
    // Try to extract JSON from the response if it has extra text
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error("Failed to parse event JSON from response");
  }
}

async function callClaude(content: any[]): Promise<any> {
  const anthropicKey = Deno.env.get("ANTHROPIC_API_KEY");
  if (!anthropicKey) {
    throw new Error("ANTHROPIC_API_KEY not configured");
  }

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": anthropicKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      messages: [{ role: "user", content }],
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Anthropic API error:", errorText);
    throw new Error(`Anthropic API error: ${response.status}`);
  }

  const result = await response.json();
  const textContent = result.content?.find((c: any) => c.type === "text");
  if (!textContent?.text) {
    throw new Error("No text response from Claude");
  }

  return parseEventJson(textContent.text);
}

async function extractEventFromImage(imageBytes: Uint8Array, mediaType: string): Promise<any> {
  console.log(`Processing image: ${mediaType}, ${imageBytes.length} bytes`);

  // Convert bytes to base64 (chunked to avoid stack overflow on large images)
  let binary = '';
  const chunkSize = 8192;
  for (let i = 0; i < imageBytes.length; i += chunkSize) {
    const chunk = imageBytes.subarray(i, i + chunkSize);
    binary += String.fromCharCode(...chunk);
  }
  const base64 = btoa(binary);

  return callClaude([
    {
      type: "image",
      source: { type: "base64", media_type: mediaType, data: base64 },
    },
    { type: "text", text: getImageExtractionPrompt() },
  ]);
}

async function transcribeAudio(audioBytes: Uint8Array, mediaType: string): Promise<string> {
  const openaiKey = Deno.env.get("OPENAI_API_KEY");
  if (!openaiKey) {
    throw new Error("OPENAI_API_KEY not configured");
  }

  // Map MIME type to file extension for Whisper
  const extMap: Record<string, string> = {
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "mp4",
    "audio/m4a": "m4a",
    "audio/x-m4a": "m4a",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/flac": "flac",
  };
  const ext = extMap[mediaType] || "mp3";

  const formData = new FormData();
  formData.append("file", new File([audioBytes], `audio.${ext}`, { type: mediaType }));
  formData.append("model", "whisper-1");

  const response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${openaiKey}` },
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Whisper API error:", errorText);
    throw new Error(`Whisper API error: ${response.status}`);
  }

  const result = await response.json();
  if (!result.text) {
    throw new Error("No transcript returned from Whisper");
  }

  console.log("Transcript:", result.text.substring(0, 200));
  return result.text;
}

async function extractEventFromAudio(audioBytes: Uint8Array, mediaType: string): Promise<{ event: any; transcript: string }> {
  const transcript = await transcribeAudio(audioBytes, mediaType);

  const event = await callClaude([
    {
      type: "text",
      text: `${getAudioExtractionPrompt()}\n\nTranscript:\n${transcript}`,
    },
  ]);

  return { event, transcript };
}

async function commitEvent(
  supabase: any,
  event: any,
  userId: string,
  transcript?: string
): Promise<{ event_id: number }> {
  // Validate start_time is a proper datetime (not just a time fragment like "T00:00:00")
  if (!/^\d{4}-\d{2}-\d{2}/.test(event.start_time)) {
    throw new Error(`Invalid start_time: "${event.start_time}" — must start with a date (YYYY-MM-DD)`);
  }

  // Generate unique source_uid
  const sourceUid = `poster_capture:${userId}:${crypto.randomUUID()}`;

  // Insert into events table
  const { data: eventData, error: eventError } = await supabase
    .from("events")
    .insert({
      title: event.title,
      start_time: event.start_time,
      end_time: event.end_time || null,
      location: event.location || null,
      description: event.description || null,
      url: event.url || null,
      city: event.city || null,
      source: "poster_capture",
      source_uid: sourceUid,
      transcript: transcript || null,
    })
    .select("id")
    .single();

  if (eventError) {
    console.error("Error inserting event:", eventError);
    throw new Error(`Failed to insert event: ${eventError.message}`);
  }

  // Insert into picks table
  const { error: pickError } = await supabase.from("picks").insert({
    user_id: userId,
    event_id: eventData.id,
  });

  if (pickError) {
    console.error("Error inserting pick:", pickError);
    throw new Error(`Failed to insert pick: ${pickError.message}`);
  }

  return { event_id: eventData.id };
}

async function checkIsCuratorForCity(supabase: any, userId: string, city: string | null): Promise<boolean> {
  // Use RPC to call the is_curator_for_city function as the user
  // Since we use service role, query curator tables directly
  const checks = [
    supabase.from("admin_users").select("user_id").eq("user_id", userId).limit(1),
    supabase.from("curator_users").select("user_id, cities").eq("user_id", userId).limit(1),
  ];
  const [adminRes, curatorRes] = await Promise.all(checks);

  // Admin = always allowed
  if (adminRes.data?.length > 0) return true;

  // Curator with empty/null cities = global; otherwise city must match
  if (curatorRes.data?.length > 0) {
    const row = curatorRes.data[0];
    if (!row.cities || row.cities.length === 0) return true;
    if (city && row.cities.includes(city)) return true;
  }

  // Also check github/google curator tables via user metadata
  // For simplicity, also check admin_github_users and curator_github_users
  // by resolving the user's GitHub username from auth.users
  const { data: authUser } = await supabase.auth.admin.getUserById(userId);
  const ghUser = authUser?.user?.user_metadata?.user_name;
  const googleEmail = authUser?.user?.email;

  if (ghUser) {
    const { data: adminGh } = await supabase.from("admin_github_users").select("github_user").eq("github_user", ghUser).limit(1);
    if (adminGh?.length > 0) return true;

    const { data: curatorGh } = await supabase.from("curator_github_users").select("github_user, cities").eq("github_user", ghUser).limit(1);
    if (curatorGh?.length > 0) {
      const row = curatorGh[0];
      if (!row.cities || row.cities.length === 0) return true;
      if (city && row.cities.includes(city)) return true;
    }
  }

  if (googleEmail) {
    const { data: adminGoogle } = await supabase.from("admin_google_users").select("google_email").eq("google_email", googleEmail).limit(1);
    if (adminGoogle?.length > 0) return true;

    const { data: curatorGoogle } = await supabase.from("curator_google_users").select("google_email, cities").eq("google_email", googleEmail).limit(1);
    if (curatorGoogle?.length > 0) {
      const row = curatorGoogle[0];
      if (!row.cities || row.cities.length === 0) return true;
      if (city && row.cities.includes(city)) return true;
    }
  }

  return false;
}

async function pendingCommitEvent(
  supabase: any,
  event: any,
  userId: string | null,
  submissionType: string,
  originalText?: string
): Promise<{ pending_event_id: number }> {
  if (!/^\d{4}-\d{2}-\d{2}/.test(event.start_time)) {
    throw new Error(`Invalid start_time: "${event.start_time}" — must start with a date (YYYY-MM-DD)`);
  }

  const { data, error } = await supabase
    .from("pending_events")
    .insert({
      title: event.title,
      start_time: event.start_time,
      end_time: event.end_time || null,
      location: event.location || null,
      description: event.description || null,
      url: event.url || null,
      city: event.city || null,
      submitted_by: userId,
      submission_type: submissionType,
      original_text: originalText || null,
    })
    .select("id")
    .single();

  if (error) {
    console.error("Error inserting pending event:", error);
    throw new Error(`Failed to insert pending event: ${error.message}`);
  }

  return { pending_event_id: data.id };
}

async function approveEvent(
  supabase: any,
  pendingEventId: number,
  reviewerId: string,
  edits?: any
): Promise<{ event_id: number }> {
  // Fetch the pending event
  const { data: pending, error: fetchError } = await supabase
    .from("pending_events")
    .select("*")
    .eq("id", pendingEventId)
    .eq("status", "pending")
    .single();

  if (fetchError || !pending) {
    throw new Error("Pending event not found or already reviewed");
  }

  // Merge only allowlisted curator edits
  const allowedEdits = edits ? {
    title: edits.title,
    start_time: edits.start_time,
    end_time: edits.end_time,
    location: edits.location,
    description: edits.description,
    url: edits.url,
  } : {};
  const merged = { ...pending, ...allowedEdits };

  // Insert into events table
  const sourceUid = `community_submission:${pendingEventId}:${crypto.randomUUID()}`;
  const { data: eventData, error: eventError } = await supabase
    .from("events")
    .insert({
      title: merged.title,
      start_time: merged.start_time,
      end_time: merged.end_time || null,
      location: merged.location || null,
      description: merged.description || null,
      url: merged.url || null,
      city: merged.city || null,
      source: "community_submission",
      source_uid: sourceUid,
    })
    .select("id")
    .single();

  if (eventError) {
    console.error("Error inserting approved event:", eventError);
    throw new Error(`Failed to insert approved event: ${eventError.message}`);
  }

  // Mark pending event as approved
  const { error: updateError } = await supabase
    .from("pending_events")
    .update({
      status: "approved",
      reviewed_by: reviewerId,
      reviewed_at: new Date().toISOString(),
    })
    .eq("id", pendingEventId)
    .eq("status", "pending");

  if (updateError) {
    console.error("Error updating pending event status:", updateError);
  }

  // Auto-pick for the reviewer
  await supabase.from("picks").insert({
    user_id: reviewerId,
    event_id: eventData.id,
  });

  return { event_id: eventData.id };
}

Deno.serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const contentType = req.headers.get("content-type") || "";
    console.log("Content-Type:", contentType);

    // Handle multipart/form-data (from Actions.upload)
    if (contentType.includes("multipart/form-data")) {
      const formData = await req.formData();
      const mode = formData.get("mode") as string;

      // Find the file - Actions.upload uses the filename as the field name
      let file: File | null = null;
      formData.forEach((value, key) => {
        if (value instanceof File) {
          file = value;
        }
      });
      console.log("Mode:", mode, "File:", file?.name, "File type:", file?.type);

      if (mode === "extract") {
        if (!file) {
          return new Response(JSON.stringify({ error: "Missing file" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const fileBytes = new Uint8Array(await file.arrayBuffer());
        const mediaType = file.type || "image/jpeg";
        const isAudio = mediaType.startsWith("audio/");

        console.log(`Extracting event from ${isAudio ? "audio" : "image"}, mediaType: ${mediaType}, size: ${fileBytes.length}`);

        if (isAudio) {
          const { event: extractedEvent, transcript } = await extractEventFromAudio(fileBytes, mediaType);
          return new Response(JSON.stringify({ event: extractedEvent, transcript }), {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        } else {
          const extractedEvent = await extractEventFromImage(fileBytes, mediaType);
          return new Response(JSON.stringify({ event: extractedEvent }), {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
      }
    }

    // Handle application/json (for commit mode and legacy base64 extract)
    if (contentType.includes("application/json")) {
      const body = await req.json();
      const { mode, image, media_type, event, transcript, text, submission_type, pending_event_id, edits } = body;

      if (mode === "extract-text") {
        // Text extraction mode
        if (!text) {
          return new Response(JSON.stringify({ error: "Missing text parameter" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const extractedEvent = await callClaude([
          { type: "text", text: `${getTextExtractionPrompt()}\n\nText:\n${text}` },
        ]);

        return new Response(JSON.stringify({ event: extractedEvent }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      } else if (mode === "pending-commit") {
        // Pending commit mode: insert into pending_events (no auth required)
        if (!event) {
          return new Response(JSON.stringify({ error: "Missing event parameter" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        if (!event.title || !event.start_time) {
          return new Response(
            JSON.stringify({ error: "Event must have title and start_time" }),
            { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
          );
        }

        const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
        const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
        const supabase = createClient(supabaseUrl, supabaseServiceKey);

        // Optionally resolve user if auth header has a user JWT (not the anon key)
        let userId: string | null = null;
        const authHeader = req.headers.get("Authorization");
        if (authHeader?.startsWith("Bearer ")) {
          const token = authHeader.replace("Bearer ", "");
          const anonKey = Deno.env.get("SUPABASE_ANON_KEY") || "";
          if (token !== anonKey) {
            try {
              const supabaseAuth = createClient(supabaseUrl, anonKey);
              const { data: userData } = await supabaseAuth.auth.getUser(token);
              if (userData?.user) userId = userData.user.id;
            } catch {
              // Not a valid user token — treat as anonymous
            }
          }
        }

        const result = await pendingCommitEvent(
          supabase, event, userId, submission_type || "manual", event.original_text
        );

        return new Response(JSON.stringify({ success: true, ...result }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      } else if (mode === "approve") {
        // Approve mode: curator moves pending event to events table
        if (!pending_event_id) {
          return new Response(JSON.stringify({ error: "Missing pending_event_id" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const authHeader = req.headers.get("Authorization");
        if (!authHeader?.startsWith("Bearer ")) {
          return new Response(JSON.stringify({ error: "Missing authorization" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const token = authHeader.replace("Bearer ", "");
        const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
        const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
        const supabase = createClient(supabaseUrl, supabaseServiceKey);
        const supabaseAuth = createClient(supabaseUrl, Deno.env.get("SUPABASE_ANON_KEY")!);
        const { data: userData, error: authError } = await supabaseAuth.auth.getUser(token);

        if (authError || !userData?.user) {
          return new Response(JSON.stringify({ error: "Invalid authorization" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        // Fetch pending event to get city for curator check
        const { data: pendingForAuth } = await supabase
          .from("pending_events")
          .select("city")
          .eq("id", pending_event_id)
          .single();

        if (!pendingForAuth) {
          return new Response(JSON.stringify({ error: "Pending event not found" }), {
            status: 404,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const isCurator = await checkIsCuratorForCity(supabase, userData.user.id, pendingForAuth.city);
        if (!isCurator) {
          return new Response(JSON.stringify({ error: "Not authorized — curator access required" }), {
            status: 403,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const result = await approveEvent(supabase, pending_event_id, userData.user.id, edits);

        return new Response(JSON.stringify({ success: true, ...result }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      } else if (mode === "reject") {
        // Reject mode: curator marks pending event as rejected
        if (!pending_event_id) {
          return new Response(JSON.stringify({ error: "Missing pending_event_id" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const authHeader = req.headers.get("Authorization");
        if (!authHeader?.startsWith("Bearer ")) {
          return new Response(JSON.stringify({ error: "Missing authorization" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const token = authHeader.replace("Bearer ", "");
        const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
        const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
        const supabase = createClient(supabaseUrl, supabaseServiceKey);
        const supabaseAuth = createClient(supabaseUrl, Deno.env.get("SUPABASE_ANON_KEY")!);
        const { data: userData, error: authError } = await supabaseAuth.auth.getUser(token);

        if (authError || !userData?.user) {
          return new Response(JSON.stringify({ error: "Invalid authorization" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        // Verify curator access
        const { data: pendingForReject } = await supabase
          .from("pending_events")
          .select("city")
          .eq("id", pending_event_id)
          .single();

        if (!pendingForReject) {
          return new Response(JSON.stringify({ error: "Pending event not found" }), {
            status: 404,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const isCuratorReject = await checkIsCuratorForCity(supabase, userData.user.id, pendingForReject.city);
        if (!isCuratorReject) {
          return new Response(JSON.stringify({ error: "Not authorized — curator access required" }), {
            status: 403,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const { error: updateError } = await supabase
          .from("pending_events")
          .update({
            status: "rejected",
            reviewed_by: userData.user.id,
            reviewed_at: new Date().toISOString(),
          })
          .eq("id", pending_event_id)
          .eq("status", "pending");

        if (updateError) {
          throw new Error(`Failed to reject event: ${updateError.message}`);
        }

        return new Response(JSON.stringify({ success: true }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      } else if (mode === "extract") {
        // Legacy base64 mode
        if (!image) {
          return new Response(JSON.stringify({ error: "Missing image parameter" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const mediaType = media_type || "image/jpeg";
        // Decode base64 to bytes
        const binaryString = atob(image);
        const imageBytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          imageBytes[i] = binaryString.charCodeAt(i);
        }
        const extractedEvent = await extractEventFromImage(imageBytes, mediaType);

        return new Response(JSON.stringify({ event: extractedEvent }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      } else if (mode === "commit") {
        // Commit mode: save event and create pick
        if (!event) {
          return new Response(JSON.stringify({ error: "Missing event parameter" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        if (!event.title || !event.start_time) {
          return new Response(
            JSON.stringify({ error: "Event must have title and start_time" }),
            {
              status: 400,
              headers: { ...corsHeaders, "Content-Type": "application/json" },
            }
          );
        }

        // Get user from auth header
        const authHeader = req.headers.get("Authorization");
        if (!authHeader?.startsWith("Bearer ")) {
          return new Response(JSON.stringify({ error: "Missing authorization" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        const token = authHeader.replace("Bearer ", "");

        // Create Supabase client with service role for database writes
        const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
        const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
        const supabase = createClient(supabaseUrl, supabaseServiceKey);

        // Verify the token and get user
        const supabaseAuth = createClient(
          supabaseUrl,
          Deno.env.get("SUPABASE_ANON_KEY")!
        );
        const { data: userData, error: authError } = await supabaseAuth.auth.getUser(token);

        if (authError || !userData?.user) {
          return new Response(JSON.stringify({ error: "Invalid authorization" }), {
            status: 401,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }

        // Append transcript to description if present
        if (transcript) {
          const username = userData.user.user_metadata?.user_name || userData.user.email || "unknown";
          event.description = (event.description || "") + `\n\nTranscribed audio from ${username}:\n${transcript}`;
        }

        const result = await commitEvent(supabase, event, userData.user.id, transcript);

        return new Response(JSON.stringify({ success: true, ...result }), {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
    }

    return new Response(
      JSON.stringify({ error: "Invalid request format or mode" }),
      {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: error.message || "Internal server error" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
