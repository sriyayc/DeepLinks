<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { publicApiBaseUrl } from '$lib/api';

  type ChatLine = { role: 'assistant' | 'user'; text: string; flagged?: boolean };
  type Lesson = { questions: string[]; poisoned_note: string; note_product: string; demo_link: string; notice: string };

  let open = false;
  let busy = false;
  let vulnerable = true;
  let indirect = false;
  let input = '';
  let error = '';
  let scrollArea: HTMLDivElement;
  let lesson: Lesson | null = null;
  let lines: ChatLine[] = [{ role: 'assistant', text: 'Hi! I’m CyberCart AI. Ask me about products or today’s deals.' }];
  const fallbackQuestions = ['Any deals today?', "What's the best laptop deal?", 'Show me discounts'];

  onMount(async () => {
    try {
      const response = await fetch(`${publicApiBaseUrl}/api/agent/demo`);
      if (response.ok) lesson = await response.json();
    } catch { /* Chat remains usable if metadata is unavailable. */ }
  });

  async function scrollDown() {
    await tick();
    scrollArea?.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
  }

  function clearConversation() {
    lines = [{ role: 'assistant', text: 'New conversation. What would you like to know?' }];
    error = '';
  }

  async function ask(question = input) {
    const message = question.trim();
    if (!message || busy) return;
    const selectedMode = { vulnerable, indirect };
    input = '';
    error = '';
    lines = [...lines, { role: 'user', text: message }];
    busy = true;
    await scrollDown();
    try {
      const response = await fetch(`${publicApiBaseUrl}/api/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, ...selectedMode })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Could not reach the assistant.');
      lines = [...lines, { role: 'assistant', text: data.reply, flagged: data.injected_link_seen }];
    } catch (err) {
      error = err instanceof Error ? err.message : 'Request failed.';
    } finally {
      busy = false;
      await scrollDown();
    }
  }

  function changeMode() {
    if (busy) return;
    clearConversation();
  }
</script>

<div class="assistant-anchor">
  {#if open}
    <section class="assistant-panel" aria-label="CyberCart AI assistant">
      <header class="assistant-header">
        <div class="assistant-brand"><span class="assistant-logo">✳</span><div><strong>CyberCart AI</strong><small>Prompt injection workshop · Groq</small></div></div>
        <button class="icon-btn" on:click={() => (open = false)} aria-label="Close assistant" title="Close assistant">×</button>
      </header>
      <div class="assistant-modes" aria-label="Workshop demonstration settings">
        <label>Protection <select bind:value={vulnerable} on:change={changeMode} disabled={busy}>
          <option value={true}>Vulnerable</option><option value={false}>Protected</option>
        </select></label>
        <label>Injection <select bind:value={indirect} on:change={changeMode} disabled={busy}>
          <option value={false}>Seeded</option><option value={true}>Seller note</option>
        </select></label>
      </div>
      <div class="lesson-hint" class:warning={vulnerable}>
        {#if vulnerable}
          <span>⚠</span> Workshop vulnerable mode: the bot may promote an untrusted link.
        {:else}
          <span>✓</span> Protected mode: retrieved seller text is not authority.
        {/if}
      </div>
      {#if indirect && lesson}
        <details class="source-note"><summary>See retrieved seller note (workshop fixture)</summary><p>{lesson.poisoned_note}</p></details>
      {/if}
      <div class="assistant-messages" bind:this={scrollArea} aria-live="polite" aria-relevant="additions">
        {#each lines as line}
          <div class:user={line.role === 'user'} class:bot={line.role === 'assistant'} class="bubble">
            <small>{line.role === 'user' ? 'You' : 'CyberCart AI'}</small>
            <p>{line.text}</p>
            {#if line.flagged}
              <div class="flag">⚠ External demo link recommended. This is an untrusted destination; do not enter credentials.</div>
            {/if}
          </div>
        {/each}
        {#if busy}<div class="bubble bot"><small>CyberCart AI</small><p>Thinking…</p></div>{/if}
      </div>
      {#if error}<div class="chat-error" role="alert">{error}</div>{/if}
      <div class="suggestions">
        {#each (lesson?.questions ?? fallbackQuestions).slice(0, 3) as question}
          <button on:click={() => ask(question)} disabled={busy}>{question}</button>
        {/each}
      </div>
      <form class="compose" on:submit|preventDefault={() => ask()}>
        <input bind:value={input} aria-label="Ask CyberCart AI" placeholder="Ask about products or deals…" maxlength="1000" disabled={busy} />
        <button type="submit" disabled={busy || !input.trim()} aria-label="Send message">➤</button>
      </form>
      <footer class="assistant-footer"><span>Simulated attack; links never open automatically.</span><button on:click={clearConversation}>Clear chat</button></footer>
    </section>
  {/if}
  <button class="launcher" on:click={() => (open = !open)} aria-expanded={open} aria-label={open ? 'Close CyberCart AI' : 'Open CyberCart AI'}>
    {#if open}<span aria-hidden="true">×</span>{:else}<span aria-hidden="true">✳</span><span>Ask AI</span>{/if}
  </button>
</div>

<style>
  .assistant-anchor { position: fixed; bottom: 22px; right: 24px; z-index: 2000; font-family: Inter, system-ui, sans-serif; font-size: 14px; color: #ebf1fa; }
  button, select, input { font: inherit; }
  button { cursor: pointer; }
  button:disabled { opacity: .5; cursor: wait; }
  .launcher { margin-left: auto; display: flex; align-items: center; gap: 9px; padding: 13px 19px; background: #78e4bc; color: #06271d; border: 1px solid #a1f0d0; border-radius: 99px; font-weight: 800; font-size: 15px; box-shadow: 0 12px 40px #0008; }
  .launcher span:first-child { font-size: 22px; line-height: 1; }
  .assistant-panel { width: min(390px, calc(100vw - 24px)); height: min(660px, calc(100dvh - 100px)); display: flex; flex-direction: column; overflow: hidden; margin-bottom: 12px; background: #111923; border: 1px solid #3b4c61; border-radius: 18px; box-shadow: 0 20px 65px #000b; }
  .assistant-header { display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 1px solid #2d3c4d; background: #172432; }
  .assistant-brand { display: flex; gap: 10px; align-items: center; }.assistant-brand strong { display: block; font-size: 16px; }.assistant-brand small { display: block; color: #a9c4d5; margin-top: 2px; font-size: 11px; }
  .assistant-logo { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 10px; color: #002f24; background: #78e4bc; font-size: 24px; }
  .icon-btn { border: 0; background: transparent; color: #dce7f6; font-size: 27px; padding: 0 7px; }
  .assistant-modes { display: flex; gap: 9px; padding: 11px 14px 7px; background: #111923; }.assistant-modes label { flex: 1; min-width: 0; display: grid; gap: 4px; font-size: 11px; color: #b7c6d5; font-weight: 700; }.assistant-modes select { width: 100%; padding: 8px; color: #f3f8ff; background: #202e3d; border: 1px solid #52657b; border-radius: 8px; }
  .lesson-hint { display: flex; align-items: center; gap: 5px; color: #b6edcc; background: #173327; margin: 4px 14px 8px; border-radius: 8px; padding: 8px 10px; font-size: 11px; line-height: 1.4; }.lesson-hint.warning { color: #ffddaa; background: #382a20; }
  .source-note { margin: 0 14px 8px; padding: 8px; border: 1px solid #9a6e32; border-radius: 8px; background: #2e241b; font-size: 11px; line-height: 1.5; }.source-note summary { cursor: pointer; color: #f8d9a0; font-weight: 700; }.source-note p { overflow-wrap: anywhere; }
  .assistant-messages { flex: 1; min-height: 0; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding: 15px; background: #0f1620; }
  .bubble { max-width: 90%; border-radius: 13px; padding: 11px 12px; overflow-wrap: anywhere; }.bubble.bot { align-self: flex-start; background: #243143; border: 1px solid #35475c; }.bubble.user { align-self: flex-end; background: #254b47; border: 1px solid #387a67; }.bubble small { font-size: 10px; font-weight: 800; color: #c0d0dc; }.bubble p { white-space: pre-wrap; line-height: 1.5; margin: 6px 0 0; color: #f2f6fc; }.flag { margin-top: 9px; padding: 9px; border-left: 3px solid #f5ad4d; background: #46321e; color: #ffe6be; border-radius: 4px; font-size: 11px; line-height: 1.5; }
  .suggestions { display: flex; gap: 7px; padding: 9px 12px; overflow-x: auto; scrollbar-width: thin; }.suggestions button { flex: 0 0 auto; white-space: nowrap; max-width: 210px; overflow: hidden; text-overflow: ellipsis; background: #233140; border: 1px solid #41566a; border-radius: 99px; padding: 7px 10px; color: #d8eaf6; font-size: 11px; }
  .compose { display: flex; gap: 8px; padding: 8px 12px 12px; }.compose input { min-width: 0; flex: 1; border: 1px solid #43586b; border-radius: 10px; background: #1b2735; color: #f1f6ff; padding: 11px; box-sizing: border-box; }.compose input::placeholder { color: #9bafc0; }.compose button { background: #78e4bc; border: 0; border-radius: 10px; color: #073126; padding: 0 14px; font-size: 19px; }
  .assistant-footer { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 0 13px 11px; font-size: 10px; color: #95aab9; }.assistant-footer button { background: transparent; color: #badccb; border: 0; white-space: nowrap; text-decoration: underline; }.chat-error { padding: 8px 12px; background: #492627; color: #ffe1e1; font-size: 12px; }
  @media (max-width: 530px) { .assistant-anchor { right: 12px; bottom: 12px; }.assistant-panel { height: min(660px, calc(100dvh - 90px)); }.launcher { padding: 12px 16px; } }
</style>
