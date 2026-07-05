# Playtest — Ledger Wave (2026-07-05)

**Tester:** _______  **Date:** _______  **Build/commit:** `a48ab65`+ (`main`)

> First play since the "Big Pause" **plus** five new mechanic lanes (scoring rewire,
> determinism, replay, seed schedules, the Liability Ledger + its player-facing UI).
>
> **Division of labour:**
> - **This doc** = the *new* mechanics + a boot smoke pass + *feel*. Work it top-to-bottom.
> - **`QA_PLAYTHROUGH_v0.11.md`** = the general regression sweep (research quality, risk
>   pools/F3, difficulty, scenarios, conferences/T, events, accessibility, debug). Run it
>   after §1–2 here.
> - **The automated exploit sweep** (`docs/qa/EXPLOIT_SWEEP_2026-07-05.md`, landing
>   separately) measures *balance/dominant strategies* with bots — so here, judge **feel**,
>   not numbers. If something feels overpowered, note it; the bots will have quantified it.
>
> Capture as you go (don't wait for the end). **F8** files a bug with state attached.

---

## §0 · Boot smoke — DO FIRST (BL-1's click paths weren't verified in CI)
- [X] Game launches to the welcome screen, no console errors.
- [ The game spawwns with an event immediately, which feels odd before I've begun to start my first turn cycle] Start a **Standard** game → loads to the main UI, no errors.
- [ Ledger just says 'ledger: clean'] The **compact ledger summary** shows under the doom trend (`Ledger: $X owed | due Nt | Y secret`).
- [ ] A **Financing** action is present in the action list.
- [Financing thing is there, needs an icon, prob can use one of the spares>. When I click I get the ledger screen; the ledger screen looks bad and could look better if it looked like one of the other submenus. When I click on the leger in more detail, the part that says 'clean books. every debt here will end up as a bill' the text is stuck on the left hand side and is scrollinng with a little scrollbar, looks weird.  ] **Financing → "View Ledger"** opens the ledger screen *(this is the specific
      unverified click path)*; closes via **[X]** / **ESC**.

If any of §0 fails, stop and note it — that's a BL-1 bug, not a design issue.
Notes: _______________________________________________________________

---

## §1 · The Liability Ledger loop (the new flagship — WS-1 + BL-1)

### Take on liabilities (Financing submenu)
- [Works ] **Take Loan** — +$50k now; a payable entry appears, due in ~4 turns.
- [ Works] **Funding-with-Strings** — +$40k; a governance-obligation entry appears.
- [Works, but the text is running into the same formatting and scrolling issues as its parent text above  ] **Desperation Lever** — doom drops now; a **secret**, compounding governance liability appears (you can see your *own* secrets).
- [ ] **Contractor** — +2 AP; a small governance rider entry appears.

### The ledger screen reads clearly
- [NBo. It would be better I think if it was broken up more clearly into a table ] Each entry shows source, currency, principal, **due Nt**, interest, secret flag, side (payable/receivable).
- [ Yes, good enough for now. General bug, I seem to be able to hire safety researcher but not capabilities researcher (maybe) but DEFINITELY not interpretability researcher. it seems to be having issues with hire_intereptability_researcher which makes me think that was set up wrong, why would you have such a specific way of hiring people. Shold be more modular. Bad smell. Chick for philosphical outdate of this entire area.] Outstanding totals shown; compact summary **reddens** as secrets mount.

### Fuses, interest, billing (advance several turns)
- [No, something happened in here and all my money disappeared?


[GameManager] All events resolved - transitioning to action selection
[MainUI] Phase changed: action_selection
[MainUI] Populating 13 actions as icon buttons
[MainUI] Action Discovery: 10 unlocked, 3 locked (hidden)
[MainUI] Event resolved, queue empty
[MainUI] Updated button states: queue_size=1, buttons_disabled=false
[MainUI] Updated button states: queue_size=0, buttons_disabled=true
[INFO/TURN] Ending turn [Context: {"actions":["pass_turn"],"queued_actions":1,"turn":5}]
[GameManager] Executing turn...
[MainUI] Phase changed: turn_end
[VerificationTracker] Action: pass_turn → 47104b3f872ecf6f...
[VerificationTracker] Turn 5 end → 332dfcb3ad60463d...
[MainUI] Action executed: { "success": true, "message": "Passed turn (no actions taken)" }
[MainUI] Action executed: { "success": true, "message": "DeepSafety: hire_researcher, safety_research" }
[MainUI] Action executed: { "success": true, "message": "CapabiliCorp: publish_paper, publish_paper, buy_compute" }
[MainUI] Action executed: { "success": true, "message": "StealthAI: safety_research" }
[MainUI] Action executed: { "success": true, "message": "Doom 55.3 → 56.9 (change: +1.6)\n  └─ base: +1.0, momentum: +0.6\n  └─ Momentum: doom spiral (0.6) (0.6)" }
[MainUI] State updated: { "money": 345000.0, "compute": 100.0, "research": 21.0, "research_quality_mode": "standard", "papers": 0.0, "reputation": 50.0, "governance": 50.0, "ledger": { "outstanding_payable": 292968.75, "outstanding_receivable": 0.0, "entry_count": 2, "secret_count": 0, "soonest_fuse": 0, "death_attribution": [] }, "doom": 56.86202971648, "doom_history": [50.0, 51.138, 52.40296, 53.7847232, 55.273945344, 56.86202971648], "doom_system": { "doom": 56.86202971648, "doom_velocity": 0.83193, "doom_momentum": 0.58808437248, "doom_trend": "increasing", "doom_status": "danger", "momentum_description": "doom spiral (0.6)", "doom_sources": { "base": 1.0, "capabilities": 0.0, "rivals": 0.0, "safety": 0.0, "unproductive": 0.0, "events": 0.0, "momentum": 0.58808437248, "technical_debt": 0.0, "specializations": 0.0, "cascades": 0.0, "market_pressure": 0.0 } }, "risk_system": { "pools": { "capability_overhang": 0.0, "research_integrity": 0.0, "regulatory_attention": 0.0, "public_awareness": 0.0, "insider_threat": 0.0, "financial_exposure": 10.0 }, "thresholds_triggered": { "capability_overhang": 0, "research_integrity": 0, "regulatory_attention": 0, "public_awareness": 0, "insider_threat": 0, "financial_exposure": 0 }, "history": [{ "turn": 1, "pool": "financial_exposure", "change": 5.0, "source": "debt", "new_value": 5.0 }, { "turn": 1, "pool": "financial_exposure", "change": 5.0, "source": "debt", "new_value": 10.0 }] }, "action_points": 3, "committed_ap": 0, "reserved_ap": 0, "available_ap": 3, "event_ap": 0, "stationery": 100.0, "technical_debt": 0.0, "tech_debt_status": "minimal", "tech_debt_color": (0.3, 0.8, 0.3, 1.0), "tech_debt_failure_chance": 0.0, "safety_researchers": 0, "capability_researchers": 0, "compute_engineers": 0, "managers": 0, "total_staff": 0, "management_capacity": 9, "unmanaged_count": 0, "turn": 5, "doom_integral": 230.53834173952, "turn_display": "Week 2 | Mon Jul 10, 2017 | Day 1/5", "calendar": { "year": 2017, "month": 7, "day": 10, "weekday": "Monday", "week_number": 2, "day_of_week": 1, "quarter": 3 }, "game_over": false, "victory": false, "rival_labs": ["DeepSafety (safety): $380k, 80 rep, 62.0 safety, 0.0 caps", "CapabiliCorp (capabilities): $570k, 80 rep, 0.0 safety, 45.0 caps", "StealthAI: Rumored to exist."], "has_cat": false, "purchased_upgrades": [], "researchers": [], "candidate_pool": [{ "name": "Morgan Rodriguez", "specialization": "safety", "skill_level": 2, "salary_expectation": 64649.0514278412, "current_salary": 64649.0514278412, "base_productivity": 1.1, "loyalty": 54, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Jordan Patel", "specialization": "safety", "skill_level": 1, "salary_expectation": 64448.2226371765, "current_salary": 64448.2226371765, "base_productivity": 0.8, "loyalty": 68, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Owen Moore", "specialization": "interpretability", "skill_level": 6, "salary_expectation": 59118.6944246292, "current_salary": 59118.6944246292, "base_productivity": 1.1, "loyalty": 60, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Gray Zhang", "specialization": "interpretability", "skill_level": 7, "salary_expectation": 63089.213848114, "current_salary": 63089.213848114, "base_productivity": 1.2, "loyalty": 64, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }], "paper_submissions": [], "attended_conferences": [] }
[GameManager] Starting turn 6
[VerificationTracker] RNG: candidate_spawn=0.428315 → 5d2e05126c88a2c3...
[VerificationTracker] RNG: candidate_spec=0.106816 → d8d619d5001ed283...
[VerificationTracker] RNG: trait_positive=0.090411 → 95ec77d37f4eee87...
[VerificationTracker] RNG: trait_positive_select=1.000000 → 583e2996703e5471...
[VerificationTracker] RNG: trait_negative=0.748883 → 15297da3255027e8...
[VerificationTracker] RNG: event_talent_recruitment=0.069523 → 0bca9a58354da899...
[VerificationTracker] RNG: event_compute_deal=0.321782 → 0b9794fdb52bfabb...
[VerificationTracker] RNG: event_hist_arxiv_42706567777fd6de=0.330993 → e2ab31126c3e47a5...
[VerificationTracker] RNG: event_hist_arxiv_26679affba27c265=0.916948 → 4e862544da2bcf37...
[VerificationTracker] RNG: event_hist_arxiv_3d2e35721e7e6af2=0.939757 → 3e8e198dc0cb05a7...
[VerificationTracker] RNG: event_hist_arxiv_e0208f404de76bd7=0.042927 → c6eb7bb2f25c25cb...
[VerificationTracker] RNG: event_hist_arxiv_dc62ec723cf1430d=0.346123 → 361fa65ea757f2b6...
[VerificationTracker] RNG: event_hist_arxiv_9888ab8acacc8f4a=0.105836 → 6966f467c80a7141...
[VerificationTracker] RNG: event_hist_arxiv_3bc060c075113a3a=0.728886 → 80fb5272ec10981c...
[VerificationTracker] RNG: event_hist_arxiv_ac6144846c25f722=0.695789 → fea9c4566ae01ce9...
[VerificationTracker] RNG: event_hist_arxiv_abbee081bc544819=0.813426 → e3123973f89eabf5...
[VerificationTracker] RNG: event_hist_arxiv_f0e7df67a2fa5a45=0.595005 → 6a4ebc3179389c42...
[VerificationTracker] RNG: event_hist_arxiv_5bba428001708f8d=0.191516 → c0097bed97994961...
[VerificationTracker] RNG: event_hist_arxiv_259e8b768252584d=0.720772 → 78c5732d5e86f9d8...
[VerificationTracker] RNG: event_hist_arxiv_1781dfeed21085a6=0.620254 → f1e29641dfe69ef1...
[VerificationTracker] RNG: event_hist_arxiv_b61d7e33ba6251a4=0.245690 → d1704e8c854f045d...
[VerificationTracker] RNG: event_hist_arxiv_7e5e07b1807afa4e=0.730562 → 736ea5710d0d866f...
[VerificationTracker] RNG: event_hist_arxiv_cab1fd1544e648fd=0.007960 → b9db5634d9139834...
[VerificationTracker] RNG: event_hist_arxiv_9c5d157ee6114e5f=0.078926 → 31d565dd08c3084d...
[VerificationTracker] RNG: event_hist_arxiv_901b2797a974e580=0.947715 → 5fca347c58d7f7fd...
[VerificationTracker] RNG: event_hist_arxiv_caf3b68cdb135855=0.318159 → a20deedf0df17456...
[VerificationTracker] RNG: event_hist_arxiv_402f917ef1f85b47=0.770629 → a93ccbed833f37ff...
[VerificationTracker] RNG: event_hist_arxiv_db731640470abad7=0.917727 → 166732cabfa7332d...
[VerificationTracker] RNG: event_hist_arxiv_d0d350b2ac6e04b8=0.778115 → 5aabeee873bfd1ff...
[VerificationTracker] RNG: event_hist_arxiv_26e147e49fc695c9=0.372369 → 8d7d85ceb60a4b0b...
[VerificationTracker] RNG: event_hist_arxiv_beb12a23a4297645=0.684559 → e462d4f3e83a3998...
[VerificationTracker] RNG: event_hist_arxiv_0e186b0d516bdeb5=0.127636 → 24681eca81a1c97f...
[VerificationTracker] RNG: event_hist_arxiv_90075e5d06ca1445=0.861951 → 171d4fe5df5d58bf...
[VerificationTracker] RNG: event_hist_arxiv_3f2a112d14cc4080=0.589902 → 2c1b9f123bc90004...
[VerificationTracker] RNG: event_hist_arxiv_b995fa8df519db15=0.474820 → 4916c61eebd754f7...
[VerificationTracker] RNG: event_hist_arxiv_7cdb1233cf82deb9=0.818956 → 70e89150c8c4e904...
[VerificationTracker] RNG: event_hist_arxiv_05f3a92ca4a98b9f=0.038235 → ea39c7b09758ba04...
[VerificationTracker] RNG: event_hist_arxiv_a8804756ba4b9e2c=0.188574 → 6000aa584b555f69...
[VerificationTracker] RNG: event_hist_arxiv_b05147510dbab92f=0.946098 → b10e47063d84e69b...
[VerificationTracker] RNG: event_hist_arxiv_17f6f61338a0d2b0=0.009738 → 5d96c01ed4fe23b1...
[VerificationTracker] RNG: event_hist_arxiv_858b9038e0a18fff=0.728724 → 83427c526ca1da59...
[VerificationTracker] RNG: event_hist_arxiv_7065ba6b881fd64f=0.218617 → 53beb226e5f8cde2...
[VerificationTracker] RNG: event_hist_arxiv_21f2bad360e8a7d2=0.780882 → b9c5d73e25823db7...
[VerificationTracker] RNG: event_hist_arxiv_73592b70a3f5a792=0.382066 → 44136d8d9ab0c083...
[VerificationTracker] RNG: event_hist_arxiv_838c66e61a6f18fb=0.229643 → 8b852f1d6e666bb8...
[VerificationTracker] RNG: event_hist_arxiv_4b13c4aa7548bc21=0.420277 → 47f2f3f032efedf1...
[VerificationTracker] RNG: event_hist_arxiv_4d20560a864f229f=0.877600 → 4ad29540e6358942...
[VerificationTracker] RNG: event_hist_arxiv_846a5ff7a4b4af28=0.399602 → a76af90a55929877...
[VerificationTracker] RNG: event_hist_arxiv_c6b7c317d780f22b=0.368626 → 675ae39a0e68f302...
[VerificationTracker] RNG: event_hist_arxiv_267f825a372778dc=0.943780 → eb422ccfc2df6442...
[VerificationTracker] RNG: event_hist_arxiv_22c9d63fe77ad418=0.307663 → e3fe87be028f680c...
[VerificationTracker] RNG: event_hist_arxiv_784d797528d0ab87=0.906982 → 4283772a16298008...
[VerificationTracker] RNG: event_hist_arxiv_be90c7a8998cd326=0.320728 → 724dcd31019baff8...
[VerificationTracker] Event: talent_recruitment (random) → 961603af46d27d88...
[VerificationTracker] Event: government_regulation (threshold) → 1c10a9e5ec31946a...
[VerificationTracker] Event: hist_arxiv_e0208f404de76bd7 (random) → e9cc501802dccb04...
[VerificationTracker] Event: hist_arxiv_cab1fd1544e648fd (random) → af19e8a0bc14d6fd...
[VerificationTracker] Event: hist_arxiv_05f3a92ca4a98b9f (random) → 3b97710238e53879...
[VerificationTracker] Event: hist_arxiv_17f6f61338a0d2b0 (random) → 459f94429bf9e442...
[MainUI] Phase changed: turn_start
[MainUI] Action executed: { "success": true, "message": "Turn 6 started" }
[MainUI] Action executed: { "success": true, "message": "Action Points: 3 (base 3 + 0 from 0 staff)" }
[MainUI] Action executed: { "success": true, "message": "1 new candidate(s) available for hire (5 total in pool)" }
[MainUI] Action executed: { "success": true, "message": "6 event(s) require attention!" }
[MainUI] State updated: { "money": 0.0, "compute": 100.0, "research": 21.0, "research_quality_mode": "standard", "papers": 0.0, "reputation": 7.578125, "governance": 50.0, "ledger": { "outstanding_payable": 0.0, "outstanding_receivable": 0.0, "entry_count": 2, "secret_count": 0, "soonest_fuse": -1, "death_attribution": [{ "source": "loan", "currency": "money", "magnitude": 21210.9375 }] }, "doom": 56.86202971648, "doom_history": [50.0, 51.138, 52.40296, 53.7847232, 55.273945344, 56.86202971648], "doom_system": { "doom": 56.86202971648, "doom_velocity": 0.83193, "doom_momentum": 0.58808437248, "doom_trend": "increasing", "doom_status": "danger", "momentum_description": "doom spiral (0.6)", "doom_sources": { "base": 1.0, "capabilities": 0.0, "rivals": 0.0, "safety": 0.0, "unproductive": 0.0, "events": 0.0, "momentum": 0.58808437248, "technical_debt": 0.0, "specializations": 0.0, "cascades": 0.0, "market_pressure": 0.0 } }, "risk_system": { "pools": { "capability_overhang": 0.0, "research_integrity": 0.0, "regulatory_attention": 0.0, "public_awareness": 0.0, "insider_threat": 0.0, "financial_exposure": 10.0 }, "thresholds_triggered": { "capability_overhang": 0, "research_integrity": 0, "regulatory_attention": 0, "public_awareness": 0, "insider_threat": 0, "financial_exposure": 0 }, "history": [{ "turn": 1, "pool": "financial_exposure", "change": 5.0, "source": "debt", "new_value": 5.0 }, { "turn": 1, "pool": "financial_exposure", "change": 5.0, "source": "debt", "new_value": 10.0 }] }, "action_points": 3, "committed_ap": 0, "reserved_ap": 0, "available_ap": 3, "event_ap": 0, "stationery": 100.0, "technical_debt": 0.0, "tech_debt_status": "minimal", "tech_debt_color": (0.3, 0.8, 0.3, 1.0), "tech_debt_failure_chance": 0.0, "safety_researchers": 0, "capability_researchers": 0, "compute_engineers": 0, "managers": 0, "total_staff": 0, "management_capacity": 9, "unmanaged_count": 0, "turn": 6, "doom_integral": 230.53834173952, "turn_display": "Week 2 | Tue Jul 11, 2017 | Day 2/5", "calendar": { "year": 2017, "month": 7, "day": 11, "weekday": "Tuesday", "week_number": 2, "day_of_week": 2, "quarter": 3 }, "game_over": false, "victory": false, "rival_labs": ["DeepSafety (safety): $380k, 80 rep, 62.0 safety, 0.0 caps", "CapabiliCorp (capabilities): $570k, 80 rep, 0.0 safety, 45.0 caps", "StealthAI: Rumored to exist."], "has_cat": false, "purchased_upgrades": [], "researchers": [], "candidate_pool": [{ "name": "Morgan Rodriguez", "specialization": "safety", "skill_level": 2, "salary_expectation": 64649.0514278412, "current_salary": 64649.0514278412, "base_productivity": 1.1, "loyalty": 54, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Jordan Patel", "specialization": "safety", "skill_level": 1, "salary_expectation": 64448.2226371765, "current_salary": 64448.2226371765, "base_productivity": 0.8, "loyalty": 68, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Owen Moore", "specialization": "interpretability", "skill_level": 6, "salary_expectation": 59118.6944246292, "current_salary": 59118.6944246292, "base_productivity": 1.1, "loyalty": 60, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Gray Zhang", "specialization": "interpretability", "skill_level": 7, "salary_expectation": 63089.213848114, "current_salary": 63089.213848114, "base_productivity": 1.2, "loyalty": 64, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Lane Brown", "specialization": "safety", "skill_level": 5, "salary_expectation": 60588.2098674774, "current_salary": 60588.2098674774, "base_productivity": 1.0, "loyalty": 44, "burnout": 0.0, "turns_employed": 0, "traits": ["team_player"], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }], "paper_submissions": [], "attended_conferences": [] }
[GameManager] 6 event(s) triggered - blocking action selection
[MainUI] === EVENT TRIGGERED: Talent Opportunity ===
[MainUI] Event queued. Queue size: 1
[MainUI] === SHOWING EVENT: Talent Opportunity ===
[MainUI] Remaining events in queue: 0
[MainUI] Created Panel for event, size: (600.0, 450.0), position: (718.5, 315.0)
[MainUI] Setting active_dialog for event...
[MainUI] Event dialog opened, tracked 3 buttons
[MainUI] Adding event dialog to viewport root as top-level overlay...
[MainUI] Event dialog added and made visible: true
[MainUI] === EVENT TRIGGERED: New AI Regulation Proposed ===
[MainUI] Event queued. Queue size: 1
[MainUI] Event added to queue, will show after current event resolves
[MainUI] === EVENT TRIGGERED: That is not dead which can eternal lie: the aestivation hypothesis for resolving Fermi's paradox ===
[MainUI] Event queued. Queue size: 2
[MainUI] Event added to queue, will show after current event resolves
[MainUI] === EVENT TRIGGERED: Leave no Trace: Learning to Reset for Safe and Autonomous Reinforcement Learning ===
[MainUI] Event queued. Queue size: 3
[MainUI] Event added to queue, will show after current event resolves
[MainUI] === EVENT TRIGGERED: Autonomous Agents Modelling Other Agents: A Comprehensive Survey and Open Problems ===
[MainUI] Event queued. Queue size: 4
[MainUI] Event added to queue, will show after current event resolves
[MainUI] === EVENT TRIGGERED: Constrained Policy Optimization ===
[MainUI] Event queued. Queue size: 5
[MainUI] Event added to queue, will show after current event resolves
[MainUI] === EVENT DIALOG SETUP COMPLETE ===
[MainUI] Ready for keyboard input via MainUI._input()
[VerificationTracker] Response: talent_recruitment → decline → ced39ed609662203...
[MainUI] Action executed: { "success": true, "message": "Declined recruitment opportunity", "pending_events": 5, "can_select_actions": false, "can_end_turn": false }
[MainUI] State updated: { "money": 0.0, "compute": 100.0, "research": 21.0, "research_quality_mode": "standard", "papers": 0.0, "reputation": 7.578125, "governance": 50.0, "ledger": { "outstanding_payable": 0.0, "outstanding_receivable": 0.0, "entry_count": 2, "secret_count": 0, "soonest_fuse": -1, "death_attribution": [{ "source": "loan", "currency": "money", "magnitude": 21210.9375 }] }, "doom": 56.86202971648, "doom_history": [50.0, 51.138, 52.40296, 53.7847232, 55.273945344, 56.86202971648], "doom_system": { "doom": 56.86202971648, "doom_velocity": 0.83193, "doom_momentum": 0.58808437248, "doom_trend": "increasing", "doom_status": "danger", "momentum_description": "doom spiral (0.6)", "doom_sources": { "base": 1.0, "capabilities": 0.0, "rivals": 0.0, "safety": 0.0, "unproductive": 0.0, "events": 0.0, "momentum": 0.58808437248, "technical_debt": 0.0, "specializations": 0.0, "cascades": 0.0, "market_pressure": 0.0 } }, "risk_system": { "pools": { "capability_overhang": 0.0, "research_integrity": 0.0, "regulatory_attention": 0.0, "public_awareness": 0.0, "insider_threat": 0.0, "financial_exposure": 10.0 }, "thresholds_triggered": { "capability_overhang": 0, "research_integrity": 0, "regulatory_attention": 0, "public_awareness": 0, "insider_threat": 0, "financial_exposure": 0 }, "history": [{ "turn": 1, "pool": "financial_exposure", "change": 5.0, "source": "debt", "new_value": 5.0 }, { "turn": 1, "pool": "financial_exposure", "change": 5.0, "source": "debt", "new_value": 10.0 }] }, "action_points": 3, "committed_ap": 0, "reserved_ap": 0, "available_ap": 3, "event_ap": 0, "stationery": 100.0, "technical_debt": 0.0, "tech_debt_status": "minimal", "tech_debt_color": (0.3, 0.8, 0.3, 1.0), "tech_debt_failure_chance": 0.0, "safety_researchers": 0, "capability_researchers": 0, "compute_engineers": 0, "managers": 0, "total_staff": 0, "management_capacity": 9, "unmanaged_count": 0, "turn": 6, "doom_integral": 230.53834173952, "turn_display": "Week 2 | Tue Jul 11, 2017 | Day 2/5", "calendar": { "year": 2017, "month": 7, "day": 11, "weekday": "Tuesday", "week_number": 2, "day_of_week": 2, "quarter": 3 }, "game_over": false, "victory": false, "rival_labs": ["DeepSafety (safety): $380k, 80 rep, 62.0 safety, 0.0 caps", "CapabiliCorp (capabilities): $570k, 80 rep, 0.0 safety, 45.0 caps", "StealthAI: Rumored to exist."], "has_cat": false, "purchased_upgrades": [], "researchers": [], "candidate_pool": [{ "name": "Morgan Rodriguez", "specialization": "safety", "skill_level": 2, "salary_expectation": 64649.0514278412, "current_salary": 64649.0514278412, "base_productivity": 1.1, "loyalty": 54, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Jordan Patel", "specialization": "safety", "skill_level": 1, "salary_expectation": 64448.2226371765, "current_salary": 64448.2226371765, "base_productivity": 0.8, "loyalty": 68, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Owen Moore", "specialization": "interpretability", "skill_level": 6, "salary_expectation": 59118.6944246292, "current_salary": 59118.6944246292, "base_productivity": 1.1, "loyalty": 60, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Gray Zhang", "specialization": "interpretability", "skill_level": 7, "salary_expectation": 63089.213848114, "current_salary": 63089.213848114, "base_productivity": 1.2, "loyalty": 64, "burnout": 0.0, "turns_employed": 0, "traits": [], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }, { "name": "Lane Brown", "specialization": "safety", "skill_level": 5, "salary_expectation": 60588.2098674774, "current_salary": 60588.2098674774, "base_productivity": 1.0, "loyalty": 44, "burnout": 0.0, "turns_employed": 0, "traits": ["team_player"], "jet_lag_turns": 0, "jet_lag_severity": 0.0 }], "paper_submissions": [], "attended_conferences": [] }
[MainUI] Event resolved, showing next event in queue...
[MainUI] === SHOWING EVENT: New AI Regulation Proposed ===
[MainUI] Remaining events in queue: 4
[MainUI] Created Panel for event, size: (600.0, 450.0), position: (718.5, 315.0)
[MainUI] Setting active_dialog for event...
[MainUI] Event dialog opened, tracked 3 buttons
[MainUI] Adding event dialog to viewport root as top-level overlay...
[MainUI] Event dialog added and made visible: true
[MainUI] === EVENT DIALOG SETUP COMPLETE ===
[MainUI] Ready for keyboard input via MainUI._input()
[MainUI] _input called, keycode: 82 (r), active_dialog: true, buttons: 3
[MainUI] Dialog is active and valid!
[MainUI] Looking for keycode 82 in dialog_keys, found at index: 3
[MainUI] Key index 3 out of range or not found
[MainUI] Dialog active - blocking non-dialog key: 82
[VerificationTracker] Response: government_regulation → stay_neutral → f07afb72fce6ff09...
[MainUI] Action executed: { "success": true, "message": "Stayed neutral as doom increased (+2 doom)", "pending_events": 4, "can_select_actions": false, "can_end_turn": false }
[MainUI] State updated: { "money": 0.0, "compute": 100.0, "research": 21.0, "research_quality_mode": "standard", "papers": 0.0, "reputation": 7.578125, "governance": 50.0, "ledger": { "outstanding_payable": 0.0, "outstanding_receivable": 0.0, "entry_count": 2, "secret_count": 0, "soonest_fuse": -1, "death_attribution": [{ "source": "loan", "currency": "money", "magnitude": 21210.9375 }] }, "doom": 56.86202971648, "doom_history": [50.0, 51.138, 52.40296, 53.7847232, 55.273945344, 56.86202971648], "doom_system": { "doom": 56.86202971648, "doom_velocity": 0.83193, "doom_momentum": 0.58808437248, "doom_trend": "increasing", "doom_status": "danger", "momentum_description": "doom spiral (0.6)", "doom_sources": { "base": 1.0, "capabilities": 0.0, "rivals": 0.0, "safety": 0.0, "unproductive": 0.0, "events": 0.0, "momentum": 0.58808437248, "technical_debt": 0.0, "specializations": 0.0, "cascades": 0.0, "market_pressure": 0.0 } }, "risk_system": { "pools": { "capability_overhang": 0.0, "research_integrity": 0.0, "regulatory_attention": 0.0, "public_awareness": 0.0, "insider_threat": 0.0, "financial_exposure": 10.0 }, "thresholds_triggered": { "capability_overhang": 0, "research_integrity": 0, "regulatory_attention": 0, "public_awareness": 0, "insider_threat": 0, "financial_exposure": 0 }, "history": [{ "turn": 1, "pool": "financial_exposure", "change": 5.0, "source": "debt", "new_value": 5.0 }, { "turn": 1, "pool": "financial_exposu ] A loan's fuse counts down and, when due, **bills** (money leaves).
- [This is not made explicit enough to be able to tell ] Interest **compounds** on carried entries turn-over-turn.
- [This is not made explicit enough to be able to tell] An **unpayable** bill escalates into **doom** — and the post-mortem later **attributes** it to that entry.

### Exposure & blackmail (BL-2 — the teeth)
- [Explain the sequence by whic I am able to tell this over several turns ] Over turns, a **secret** liability gets **EXPOSED** → reputation/governance damage. *Confirm it actually fires.*
- [ ] Exposure can present a **blackmail** offer (a new, worse entry) — the chain continues.

### Death by ledger
- [Explain the process by which I test this ] Lean into desperation levers/loans → you eventually die, and the **death is attributed to specific ledger entries** in the post-mortem.

### FEEL — the real question this wave exists to answer
- Is the ledger **legible**? Do you always know what you owe and when it bites?
Pip - I have no easy way of getting to the ledger from the main part of the UI.  It's nice to have something remidning me when things are due. The terms of the loan are not spelled out in this simple version, which means I'm just kind of getting magic money and then soemthing happens later. I think having the player click 'pay the bill' is a good interaction.
- Is the tension **fun** — does "spend now, the bill compounds toward death" create good decisions, or is it opaque/fiddly bookkeeping?
Not sure yet. I think the game needs to last a few more turns so I can start to think particularly about how to manage my money?
- Does the **desperation lever** feel like a real *catch-up-when-behind* lever, or a no-brainer / a trap?
The mechanic is not clear enough for me to know when to use it; I tihnk it feels a bit too generic?
- Does the game now feel **more tense and rich** than the thin pre-wave version? *(This wave's whole reason for being.)*
The game feels like it coheres more. The original mechanism of the game focused very much on a basic cyucle of scientists -> research -> papers -> reduction of doom. We've slightly shifted away from that, but we can refocus back in on that loop a little.
Notes: _______________________________________________________________
_______________________________________________________________

---

## §2 · New scoring display (WS-A — changed since you last played)
- [Yes ] End-game shows **`Turn N · <integral>`** (turns survived · doom-integral) — **not** the old composite points total.
- [Yes ] **No victory bonus**; score is turns-survived-dominant, doom-integral only as tiebreak.
- [Yes ] **Post-mortem reveal only** — no live score ticker during play.
- [Yes, the ledaerboard looks very funny with the old scores, but it's nostalgic ] Leaderboard records the run (keyed by seed + version).
- Feel: does "how many turns did you survive" read as the score you'd brag about? (The ADR-0002 thesis.)
It feels like something I would brag about more if I played the game a few more times.
Notes: _______________________________________________________________

---

## §3 · Regression since the Big Pause
- [ ] Run **`QA_PLAYTHROUGH_v0.11.md`** end-to-end (the general sweep).
- [ ] Anything that broke since you last played? Five lanes touched core (determinism,
      replay, seed schedules, ledger, scoring) — watch for regressions in events, doom,
      turn flow, save/load.
Notes: _______________________________________________________________

---

## §4 · Capture — tag every finding

| # | Tag | Area | Description | Repro / turn |
|---|-----|------|-------------|--------------|
| 1 |     |      |             |              |
| 2 |     |      |             |              |
| 3 |     |      |             |              |

**Tags:** `BUG` (→ GitHub issue / F8) · `BALANCE` (→ workshop #2; the sweep quantifies) · `FEEL` (→ workshop #2)

## Overall
- Does the ledger make the game **more tense / richer**? [ ] clearly [ ] somewhat [ ] not yet
- Most-broken thing: __Hiring people and feeling their impact still feels pretty unconnected from the game.____________  Most-promising thing: __Once we fine tune the costs and starting amounts, the game feels much closer to there being some tension____________
- Ready to show the playtester friend? [ ] Yes [ Needs work. I think I need to have more visual representation of the employees and what they're doing, because they're both the key to the game in terms of translating effort and time into work and right now they're kind of invisible] Needs work
