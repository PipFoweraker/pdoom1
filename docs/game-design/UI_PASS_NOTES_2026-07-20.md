# UI pass notes -- 2026-07-20 (Pip's playthrough)

> Fill this in as you play. Keep it FAST -- one bullet per thing, format `- [screen] note`.
> Don't fix anything mid-play; just capture. This merges with the two agent reports
> (menu-consistency + text-trap audit) into one prioritized fix pass afterward.
> Not about the office-display art (that's a separate element) -- this is the EXISTING UI.

## 1. Blank / negative space  (where could art/decoration/panels live?)
- [screen] what feels empty / what could fill it
Main screen text needs an update. We need to experiment with font options, think about licensing for that. The white text definitely needs an upgrade.
Laboratory configuration screen is missing colour and texture entirely, which feels wrong.
PLAN screen:
The background in the left and right hand sides of the screens should be different colours, so while we're still developing things it's easier for me to see where the borders are.
The bittons are centre-aligned of the thing they'r all vertically scrolling in rather than being left-bound.
The buttons for the hiring are making the vertical slice of buttons too long. We can either get rid of them entirely becauise they're handled inside the hirinng thing, or have the behaviours happen like the other buttons and make them part of the extension out of the side. In fact, I like that idea, so that menus go

ABBBCCC
A   CCC
A   CCC
A

A
A  CCC
ABBCCC
A  CCC

or something along those lines, if that makes sense, where B is the subset of options stemming from A and then C is the additional context window that expands from B if necessary onmouseover / other?

PLAN screen still:
onmousovering actions makes the 'hober over things to see details' bit jump up and down annoyingly, probably to include the extra width from displaying the costs. Let's make the colour of the context window at the bottom of the screen yet another colour, again, helps break up the playing area into zones a little.

Month review: This pops up in a way that doesn't actually let us look around and review the month, and then when we click off it, we move immediately from the end of watch back to plan. I think a more correct nehaviour is for the things to happen and then, something like, the player can look at the after action report summary if they want and click back to plan rather than being dumped there automatically? We definitely want them to be able to scroll up and look at things, though, and maybe some kind of (and this is definitely not for current build) some kind of stack-traceability or upgrade so players can see why things are happening-ish? park that last idea. not for now. The rest of it, though, yes, let's make the behaviour more palyer friendly. The summary now doesn't really do much anyway other than as a gating popup.

PLAN screen:
Maybe we can have the icons (or a smaller version, or something, but for now maybe just re-use the icons but shrink them a tiny bit or something? on the planned actions in sequence so the player has a better visual represetnation of their priority ordering, like the build queue in civ)

I am still missing icon UI's. Specifically guide me through steps to finish solving this.

## 2. UI / texture inconsistencies  (what clashes with warm-grime + the palette?)
- [element or screen] what's off -- off-palette / placeholder-looking / mismatched / stray font
Font noted bad on main screens up.
Fot in buttons need improving. I think we have fired another agent to look for missing texture and in game elements
all of the game paused menu needs a tune up. It needs a background, matching colour palette, improvements to the box, the sliders in the game all need adjustment and some graphic design elements included that at least match our colour plans and palettes, if this means work on me to fine tune and select between them, happy with that.

Any black background needs to come off black, I don't care what, I just don't want default black on my screen.
I don't think we need the whole  WATCH SCREEN permanmently telling players what's the screen's purpose is, I think they learn that from the tutorial, intro, or a text that disappears when they're not playing for the first time.

## 3. Text traps  (confusing / wrong / placeholder / ambiguous on-screen text)
- [screen] the exact text + why it's a trap

Popup notifications should not be in green, see earlier comments about ui design needing a refresh

## 4. Anything else you notice
-
This will do for now I think
