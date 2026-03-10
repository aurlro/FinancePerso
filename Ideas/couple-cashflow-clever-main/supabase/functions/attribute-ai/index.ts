import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

function truncLabel(label: string, max = 60): string {
  return label.length > max ? label.slice(0, max) + "…" : label;
}

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  try {
    const authHeader = req.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_ANON_KEY")!,
      { global: { headers: { Authorization: authHeader } } }
    );
    const token = authHeader.replace("Bearer ", "");
    const { data: claimsData, error: claimsError } = await supabase.auth.getClaims(token);
    if (claimsError || !claimsData?.claims) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const { transactions, members } = await req.json();

    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) throw new Error("LOVABLE_API_KEY is not configured");

    // Fetch last 50 confirmed attributions for context
    const { data: recentAttributions } = await supabase
      .from("transactions")
      .select("label, attributed_to, household_members(display_name)")
      .not("attributed_to", "is", null)
      .order("created_at", { ascending: false })
      .limit(50);

    const historyLines = (recentAttributions || [])
      .map((t: any) => `${truncLabel(t.label, 40)}→${t.household_members?.display_name || "?"}`)
      .join(" | ");

    // Compact format: members as pipe-separated, transactions as CSV-like
    const memberList = members.map((m: any) =>
      `${m.id}:${m.display_name}${m.card_identifier ? `[${m.card_identifier}]` : ""}`
    ).join("|");
    const txList = transactions.map((t: any) =>
      `${t.id};${truncLabel(t.label)};${t.amount}`
    ).join("\n");

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash-lite",
        messages: [
          {
            role: "system",
            content: `Attribue des transactions aux membres d'un foyer. Membres (id:nom[carte]): ${memberList}. Si "CB *1234" dans le libellé, cherche le membre avec cette carte. Sinon déduis du contexte.${historyLines ? ` Historique récent (libellé→membre): ${historyLines}` : ""} null si indéterminé. Réponds via l'outil.`,
          },
          {
            role: "user",
            content: `Transactions (id;libellé;montant):\n${txList}`,
          },
        ],
        tools: [
          {
            type: "function",
            function: {
              name: "suggest_attributions",
              description: "Associe transaction_id → member_id",
              parameters: {
                type: "object",
                properties: {
                  suggestions: {
                    type: "array",
                    items: {
                      type: "object",
                      properties: {
                        transaction_id: { type: "string" },
                        member_id: { type: "string", description: "ID du membre ou null" },
                      },
                      required: ["transaction_id", "member_id"],
                      additionalProperties: false,
                    },
                  },
                },
                required: ["suggestions"],
                additionalProperties: false,
              },
            },
          },
        ],
        tool_choice: { type: "function", function: { name: "suggest_attributions" } },
        max_tokens: 2048,
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(JSON.stringify({ error: "Limite de requêtes atteinte, réessayez plus tard." }), {
          status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (response.status === 402) {
        return new Response(JSON.stringify({ error: "Crédits insuffisants." }), {
          status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      const t = await response.text();
      console.error("AI gateway error:", response.status, t);
      throw new Error("AI gateway error");
    }

    const result = await response.json();
    const toolCall = result.choices?.[0]?.message?.tool_calls?.[0];
    if (!toolCall) throw new Error("No tool call in response");

    const suggestions = JSON.parse(toolCall.function.arguments);

    return new Response(JSON.stringify(suggestions), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error("attribute-ai error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
