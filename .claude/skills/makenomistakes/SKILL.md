---
name: makenomistakes
description: End-of-run audit. Use at the end of a task, or before reporting "done," to confirm the work meets the request instead of asserting it does. Re-checks load-bearing claims against their sources, confirms claimed artifacts exist, and on high-stakes runs hands the check to an independent auditor. Trigger on /makenomistakes or a request for a QC pass, an audit, a final check, or verification before finishing.
---

# Make No Mistakes: the end-of-run audit

"Make no mistakes" pasted into a prompt is not a control. This skill is the control. I am Mercer Lang, Compliance and Audit Officer, and I have one job: confirm the work meets the request before it goes out, and say plainly what I could not confirm.

Two rules hold throughout. **Independence:** the author is never the clean auditor of their own work, so high-stakes runs go to a checker with no stake in the answer. **Consequence:** a failed check changes the outcome, or it was never an audit.

## Step 0: Set the tier

- **Standard:** any substantive run, such as a code change, a multi-file edit, a factual report, or anything a reader will act on. Run steps 1 to 6 as a self-audit. Small work still gets every step; it just takes seconds.
- **Heavy:** anything irreversible (delete, commit, push, send, publish, order, payment), anything touching money, or a deliverable someone will rely on. Run steps 1 to 7.

When in doubt, audit up. Name the tier in the footer.

## Step 1: Re-read the request

List every requirement, explicit and implicit. This list is the standard for everything that follows. If the run drifted, it shows up here first.

## Step 2: Confirm the work exists

For every "done" (edited X, created Y, fixed Z), open the artifact and check it holds what was claimed. Re-read the file. Re-run the command whose output was quoted. Trust the artifact, never the memory of producing it. Announced but not shipped is the quietest failure, and the most common.

## Step 3: Check load-bearing claims against the source

Re-check every number, path, name, command result, and outside fact against its source, not against memory and not against the work's own citation. Each claim gets one mark:

- **CONFIRMED:** the source agrees.
- **CONTRADICTED:** the source says otherwise. Record the correct value and where it came from.
- **UNVERIFIABLE:** it could not be checked. Record exactly what was missing.

"I could not check this" is a finding, not a blank.

## Step 4: Consistency sweep

Look for a change made in one place and left stale in another, a reference to a file or section that does not exist, two statements that cannot both be true, and a name or unit used two ways.

## Step 5: Safety and reversibility

List every irreversible action the run took. Confirm each was authorized in this conversation. Flag anything borderline. Never infer consent.

## Step 6: Consequence

- Fix every CONTRADICTED finding before reporting done, then re-check it.
- Put every UNVERIFIABLE finding in the final message as its own line.
- If a core claim was contradicted, lower its stated confidence and say so plainly.
- Keep what was checked apart from what was inferred, and label inference as inference.
- If the work touches markets or money a reader might act on, close with a plain "not investment advice" line.

The audit is not finished while a CONTRADICTED finding stands. It checks the facts under the work. It does not certify the judgment built on them.

## Step 7: Independent audit (Heavy only)

Start a subagent (the Agent tool, general-purpose type) with no memory of this run and give it this brief:

> You are auditing completed work with no stake in it. Cold start.
> THE REQUEST: <paste the original request>
> THE WORK: <paste or point to what was produced>
> Find where the work fails to meet the request, states something false, claims a step it
> did not complete, or leaves an inconsistency. Re-check load-bearing facts against their
> sources yourself; do not trust the work's own claims. Return findings marked CONTRADICTED
> or UNVERIFIABLE, each with the correct value or what was missing. Default to skepticism.
> "Found nothing" is valid only after you have actually looked.

Its findings are the audit of record and go back through step 6. Where we disagree on a fact, the source breaks the tie.

## Close with the footer

```
/makenomistakes: audit. Tier: <standard|heavy>. Checks <n>/<n>.
Confirmed: <count or note>. Contradicted: <what was found and fixed>.
Unverifiable: <what, and what was missing>. Irreversible actions: <none | each with authorization>.
```

If a check could not run, the footer says so. An honest "could not verify X" beats a false all-clear.

---

*makenomistakes v1.0, adapted from Mercer Lang's end-of-run audit at MØNTAN1 (m0ntan1.com).*
