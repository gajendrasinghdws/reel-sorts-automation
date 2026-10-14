import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cfg = window.REEL_SORTS_CONFIG;
const supabase = createClient(cfg.supabaseUrl, cfg.supabasePublishableKey);

const $ = (id) => document.getElementById(id);
const setMessage = (id, text, error=false) => {
  $(id).textContent = text;
  $(id).style.color = error ? "#b91c1c" : "#166534";
};

async function refresh() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;

  const { data: accounts, error: aErr } = await supabase
    .from("instagram_accounts")
    .select("*")
    .order("created_at", { ascending: false });

  if (aErr) return setMessage("appMessage", aErr.message, true);

  $("accounts").innerHTML = accounts.map(a => `
    <div class="row">
      <span>@${escapeHtml(a.username)}</span>
      <span class="badge">${a.active ? "ACTIVE" : "PAUSED"}</span>
    </div>
  `).join("") || "<p>No accounts yet.</p>";

  const { data: reels, error: rErr } = await supabase
    .from("reels")
    .select("id,instagram_url,status,drive_file_name,youtube_video_id,created_at,error_message")
    .order("created_at", { ascending: false })
    .limit(30);

  if (rErr) return setMessage("appMessage", rErr.message, true);

  $("jobs").innerHTML = reels.map(r => `
    <div class="row">
      <div>
        <strong>${escapeHtml(r.status)}</strong>
        <div>${escapeHtml(r.drive_file_name || r.instagram_url || "")}</div>
      </div>
      <span class="badge">${r.youtube_video_id ? "YouTube ✓" : "Pending"}</span>
    </div>
  `).join("") || "<p>No jobs yet.</p>";
}

function escapeHtml(value="") {
  return value.replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[c]));
}

$("authForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const { error } = await supabase.auth.signInWithPassword({
    email: $("email").value.trim(),
    password: $("password").value
  });
  if (error) return setMessage("authMessage", error.message, true);
  setMessage("authMessage", "Logged in.");
  await renderAuth();
});

$("logoutBtn").addEventListener("click", async () => {
  await supabase.auth.signOut();
  await renderAuth();
});

$("accountForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const { data: { user } } = await supabase.auth.getUser();
  const username = $("username").value.trim().replace(/^@/, "");
  const { error } = await supabase.from("instagram_accounts").insert({
    user_id: user.id,
    username,
    normalized_username: username.toLowerCase()
  });
  if (error) return setMessage("appMessage", error.message, true);
  $("username").value = "";
  setMessage("appMessage", "Instagram account added.");
  refresh();
});

$("reelForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const { data: { user } } = await supabase.auth.getUser();
  const url = $("reelUrl").value.trim();
  const sourceKey = url.split("?")[0].replace(/\/+$/, "").toLowerCase();

  const { data: existing } = await supabase
    .from("reels").select("id").eq("user_id", user.id)
    .eq("source_key", sourceKey).limit(1);

  if (existing?.length) {
    return setMessage("appMessage", "This Reel is already queued/downloaded.", true);
  }

  const { error } = await supabase.from("reels").insert({
    user_id: user.id,
    instagram_url: url,
    source_key: sourceKey,
    status: "queued"
  });

  if (error) return setMessage("appMessage", error.message, true);
  $("reelUrl").value = "";
  setMessage("appMessage", "Reel added to queue.");
  refresh();
});

$("refreshBtn").addEventListener("click", refresh);

async function renderAuth() {
  const { data: { user } } = await supabase.auth.getUser();
  $("authCard").classList.toggle("hidden", !!user);
  $("app").classList.toggle("hidden", !user);
  $("logoutBtn").classList.toggle("hidden", !user);
  if (user) refresh();
}

supabase.auth.onAuthStateChange(() => renderAuth());
renderAuth();
