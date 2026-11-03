// #/contact: a simple form handled by Netlify Forms (no email address on the site).
// Netlify registers the form from the hidden copy in index.html; field names here must match it.
import { esc } from '../lib.js';

const TOPICS = [['question', 'A question or note'], ['tip', 'A tip: a hearing, filing, or project'], ['correction', 'A correction']];

export function contact(main, q) {
  const pick = TOPICS.some(([k]) => k === q.get('topic')) ? q.get('topic') : 'question';
  const about = q.get('about') || '';
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Contact</div>
      <h1 class="page-h">Get in <em>touch</em></h1>
      <p class="lede">Questions, tips, and corrections are all welcome. A tip about a hearing, a filing, or a new project is the most useful thing you can send. Corrections are checked against sources and noted publicly.</p>
    </header>
    <section class="sec">
      <form class="cform" name="contact" method="POST" netlify-honeypot="bot-field" novalidate>
        <input type="hidden" name="form-name" value="contact">
        <input type="hidden" name="subject" value="WV AI Watch: new message (%{submissionId})">
        <p class="hp" aria-hidden="true"><label>Leave this empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
        <fieldset>
          <legend>What's this about?</legend>
          ${TOPICS.map(([k, l]) => `<label class="radio"><input type="radio" name="topic" value="${k}"${k === pick ? ' checked' : ''}> ${esc(l)}</label>`).join('')}
        </fieldset>
        <label class="fld">Message
          <textarea name="message" rows="7" required maxlength="5000" placeholder="What should we know? Links to sources help.">${about ? esc(`About: ${about}\n\n`) : ''}</textarea>
        </label>
        <label class="fld">Your email <span class="dim">(optional, only if you'd like a reply)</span>
          <input type="email" name="email" autocomplete="email" maxlength="200">
        </label>
        <div class="cform-actions"><button type="submit" class="btn pri">Send message</button><span class="cform-status" role="status" aria-live="polite"></span></div>
        <p class="dim" style="font-size:13px;margin-top:14px">Messages go privately to the site's editor through Netlify Forms. Nothing you send is published, and contact details are never shown on the site.</p>
      </form>
    </section>
  </div>`;

  const form = main.querySelector('form'), status = main.querySelector('.cform-status'), btn = form.querySelector('button[type=submit]');
  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const msg = form.message.value.trim();
    if (!msg) { status.textContent = 'Please write a message first.'; form.message.focus(); return; }
    if (form.email.value && !form.email.checkValidity()) { status.textContent = 'That email address looks incomplete. Fix it or leave it blank.'; form.email.focus(); return; }
    btn.disabled = true; status.textContent = 'Sending…';
    try {
      const r = await fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      form.reset();
      main.querySelector('.sec').innerHTML = `<div class="side-box act" style="max-width:640px"><h4>Sent</h4><p><b>Thank you.</b> Your message is on its way to the editor. If you left an email address, expect a reply there.</p><p style="margin-top:12px"><a class="btn" href="#/">Back to the front page</a></p></div>`;
    } catch (err) {
      console.warn('contact form failed', err);
      btn.disabled = false;
      status.textContent = "That didn't go through. Please try again in a few minutes.";
    }
  });
  return 'Contact';
}
