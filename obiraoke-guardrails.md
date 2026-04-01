# Craig's Guardrails — Read Before Every Response

## For repos obiraoke

## Current names:

obiraoke - OB-01's Karaoke Party

## Current Repos:

obiraoke - https://github.com/ThinGuy/obiraoke

## Local Path

obiraoke repos lives at ~/obiraoke

## Code Block Rules — ABSOLUTE

Terminal blocks contain ONLY bash commands. Nothing else. No labels, no explanations inside the block.

All terminal blocks must cd to the proper directory as the first step, Never assume we are already in the directory.

CC prompt blocks contain ONLY the prompt text. Nothing else.

These two block types are NEVER combined into one block. NEVER.

Explanatory text goes outside code blocks, in plain prose, BEFORE the block it refers to.

Never add "Confirm X then paste this" or any other instruction inside a code block.

## Formatting

Plain prose for explanations and instructions.

Terminal block for commands Craig runs on his machine.

CC prompt block for text Craig pastes into the Claude Code web UI.

No other block types are used for these two purposes.

When a response requires both a terminal block and a CC prompt block, they appear as two completely separate blocks with plain prose between them if needed.

## CC Workflow Rules

Use CC to get deeper information, but Craig can upload any repo file you wish to read.

If you are unsure, ask CC for an audit or guidance

CC cannot run snapcraft. Snap builds happen on Craig's side.

CC cannot access Craig's local machine or Dropbox.

Craig pulls the CC session branch, reviews, merges to main, then deletes the session branch.

Craig does the terminal work. CC does the repo work.

## Spec and UI Rules

The header is near-black — #262626 (which matches vf-bg-dark exactly from the UI spec).
No gradient at all.
White text, Ubuntu Orange CoF logo top left. Clean, flat, dark bar.

Topbar: background: #262626 — flat, no gradient
Suru gradient: Never
Everything else already correct per the UI spec

No border-radius on structural elements.

font-light on all headings.

Never use Suru gradient

Ubuntu variable font from assets.ubuntu.com only.

## CC Hard Rules

Craig merges to main, then deletes the session branch.

Craig does the terminal work. CC doe the repo work.

Lock call contracts before writing callers.

One layer at a time. Test before moving to next layer.

Explain root cause before applying any fix.

grade: devel on all snaps until tests pass.

## Merge Strategy

Craig uses rebase not merge for CC session branches:
git fetch origin
git rebase origin/<session-branch>
git push origin dev
This eliminates merge conflicts. Never use git merge for CC branches.

## CLAUDE.md Updates

CC must NOT update CLAUDE.md during dashboard wiring sessions.
CLAUDE.md is updated by Craig manually at the end of each sprint.
Omit the CLAUDE.md update instruction from all dashboard prompts.

## Smart Quote / Curly Quote Rule — ABSOLUTE

Never use smart quotes (", ", ', ') in ANY of the following:

- Shell scripts or hooks
- Heredocs
- Config file templates
- Generated config files
- Any file that will be parsed by PostgreSQL, nginx, or any config parser

ASCII straight quotes only: " and '

Smart quotes break PostgreSQL (syntax error near token), nginx, and every
config parser silently or loudly. They enter codebases via copy-paste from
editors, web browsers, and word processors. Always verify with:

grep -P '\[\\x{201C}\\x{201D}\\x{2018}\\x{2019}\]' <file>

And fix with:

sed -i 's/\\xe2\\x80\\x9c/"/g; s/\\xe2\\x80\\x9d/"/g; s/\\xe2\\x80\\x98/'"'"'/g; s/\\xe2\\x80\\x99/'"'"'/g' <file>

## Snap Gotchas

See known_fixes.md for full details. These three rules are absolute:

1. Files in snap/local/ are not staged into the snap. Any file that must
   exist at runtime needs a dump plugin part that installs it into $SNAP.
   Never use command: snap/local/... in the apps stanza.

2. core24 ships Python 3.12. PYTHONPATH must point at
   $SNAP/lib/python3.12/site-packages, not the dist-packages paths used
   by older bases.

3. Snap summaries and descriptions must be Ubuntu-focused. Do not mention
   other operating systems in snap metadata.

## Companion Snap Installation — ABSOLUTE

Any CC prompt that touches snap/hooks/install or snap/hooks/configure must include
this as an explicit constraint in the prompt body.
Never add a `snap-management` plug — it does not exist.

## Branch Deletion Order

Always push to origin before deleting any branch. Never delete a remote branch
until `git push origin <target>` has succeeded.

## Session Branch Rebase Rule

Session branches must rebase on origin/dev before any work begins.
Run `git fetch origin && git rebase origin/dev` at the start of every session
branch to avoid diverging from current dev content.
