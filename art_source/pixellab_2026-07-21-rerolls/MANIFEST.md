# Re-roll sweep MANIFEST -- 2026-07-21

Approved-queue re-roll batch. Corrected approaches per
`docs/art/reviews/SWEEP_REVIEW_2026-07-17.md` (Rulings + Re-roll work queue);
run notes in `docs/art/reviews/REROLL_RUN_2026-07-21.md`. Files under
`<group>/<key>_<roll>.png`. Character sprites: `<key>_<roll>.png` is the south
rotation, other rotations `_<dir>.png`. Tilesets: `<key>.png` is the Wang atlas
(+ `<key>.metadata.json`).

| group | key | roll | pixellab id | tool |
|---|---|---|---|---|
| tilesets | floor_concrete | - | 9f3e4695-e0e2-450e-9e9f-d553ac894abd | create_topdown_tileset |
| tilesets | floor_lino | - | 6ab69350-6353-439d-99fb-e24c4f727aa7 | create_topdown_tileset |
| tilesets | floor_carpet | - | f7984b8c-8776-4b13-bac7-ab91e7dda202 | create_topdown_tileset |
| tilesets | wall_scummy | - | 6a5632a9-e56a-432c-8433-c01b784ac472 | create_topdown_tileset |
| tilesets | wall_decent | - | 3bde872f-9867-4a44-b239-3c2342aaf8ff | create_topdown_tileset |
| windows | window_frame | 1 | 4d91830b-6d1a-44e2-952e-292df7d16e59 | create_map_object |
| windows | window_frame | 2 | 3778d4cb-459a-455c-96f3-6066df1929a4 | create_map_object |
| windows | window_frame | 3 | 56f68de6-9bb5-4285-85c1-fa50eb63c666 | create_map_object |
| windows | sky_clear | 1 | 517f7ca6-ca44-4870-bb39-8935ca520549 | create_map_object |
| windows | sky_clear | 2 | d51a2c23-1217-4539-afca-c3ae3dbc172b | create_map_object |
| windows | sky_storm | 1 | f1ac4ae9-cc27-4f82-99c1-80c4c36ac2b1 | create_map_object |
| windows | sky_storm | 2 | 4392b3d1-f795-44d9-86cb-cd4bc16c20da | create_map_object |
| windows | sky_doomy | 1 | e1925248-6d35-4842-b0b1-a74c5d40d330 | create_map_object |
| windows | sky_doomy | 2 | a18f248e-26e5-45e2-98be-924e8c77e1ef | create_map_object |
| cats | cat_eldritch | 1 | ca20613e-54d0-4285-bc18-3149a2f6f069 | create_character |
| cats | cat_eldritch | 2 | d13a61ca-67d9-4606-acd5-00f36bb28858 | create_character |
| cats | cat_purple | 1 | 821531d5-8c7e-444f-84ce-0d37f884027a | create_character |
| cats | cat_purple | 2 | c82bf943-9a0e-4531-bc3d-8d940750889d | create_character |
| founder | founder_back | 1 | 91cee793-eae2-4129-bb77-c04a0162d032 | create_map_object |
| founder | founder_back | 2 | ce5b8bc6-1f9c-45f8-910b-a1905d9e5221 | create_map_object |
| founder | founder_threequarter | 1 | 3f0dcbae-0cde-4d80-9946-06447ff99a0b | create_map_object |
| kitchen | kitchen_bench_scummy | 1 | 4d994b39-8218-41a3-8539-f054db761e71 | create_map_object |
| kitchen | kitchen_bench_scummy | 2 | a06e7201-9869-447e-8c18-25c91b296836 | create_map_object |
| kitchen | kitchen_bench_decent | 1 | 17b8d152-ae88-4551-956c-671ea82a898a | create_map_object |
| kitchen | kitchen_bench_decent | 2 | bcf3a79f-603d-4709-85f4-24b0e3c3a140 | create_map_object |
| chairs | chair_mega | 1 | db9c2330-3eaa-43cc-a91a-b4e2de2482d7 | create_map_object |
| chairs | chair_mega | 2 | ca0d7ffb-9d81-4435-8eff-c0c300320e14 | create_map_object |
| chairs | chair_decent | 1 | 8db9e7d3-955e-42fd-a1c2-13024471f3de | create_map_object |
| chairs | chair_decent | 2 | 1b29e930-f0e3-48ae-827b-b68a89b8bf31 | create_map_object |
| objects | desk_mega | 1 | dd620090-31c4-4a45-9f15-6596211fea51 | create_map_object |
| objects | desk_mega | 2 | 98a7c2c3-0c7b-431b-ba05-bbdb4dcfe442 | create_map_object |
| objects | monitor_mega | 1 | ab0fc620-63eb-453f-865b-2a05461c64dd | create_map_object |
| objects | monitor_mega | 2 | ba5a3025-dee8-463b-914d-d5a74931b32b | create_map_object |
| objects | monitor_mega_startup | 1 | 236847e0-1a21-4fbb-999a-b1ad05fc2df7 | create_map_object |
| objects | monitor_mega_startup | 2 | c7524760-3c05-4309-ba14-1907f95f8466 | create_map_object |
| objects | pc_mega | 1 | 845a7223-20ab-4c4e-b2c1-56e81687de6c | create_map_object |
| objects | pc_mega | 2 | edbff351-e011-48ab-a292-59362f0c6065 | create_map_object |
| objects | server_cluster_mega | 1 | 2e8b4ca7-7806-4541-8e63-6b456fad26aa | create_map_object |
| objects | filing_cabinet | 1 | b2fd909a-bad5-4411-b30b-268d873f9e68 | create_map_object |
| objects | printer | 1 | 6d5fee5c-3d80-4ec3-a531-9875063b0395 | create_map_object |
| objects | printer | 2 | 59e74f42-6431-4ab1-9a38-a0a4c1e1c8a3 | create_map_object |
| objects | trash_recycling | 1 | 6236c0a5-6274-4f96-b2f3-60ceb16619f1 | create_map_object |
| objects | trash_recycling | 2 | 46769bcd-4762-4133-bc61-7a7fb26902e1 | create_map_object |
| objects | meeting_table | 1 | 22b69955-b7cc-44e6-ac20-acc8ea00864f | create_map_object |
| objects | meeting_table | 2 | e3cdcddb-5f1f-4d38-afab-8432dd2048d0 | create_map_object |
| objects | water_cooler | 1 | 9f1b246f-56e9-4eb3-862b-8903dbebcb72 | create_map_object |
| objects | water_cooler | 2 | 8f5dfbe6-740d-44fb-bef7-a97ba181d123 | create_map_object |
| objects | coat_rack | 1 | 59cb02ab-4f8a-4883-aebc-c1756d6873f0 | create_map_object |
| objects | coat_rack | 2 | 42cd63a8-fa7a-4647-b9f9-d281fdcb6ff4 | create_map_object |
| objects | desk_mega_screen | 1 | 86afa0cf-c0b2-4bf2-a904-528ab4df6050 | create_map_object |
| objects | door_scummy | 1 | afcb43e1-fc74-4f30-89c0-45e64421aa7e | create_map_object |
| objects | door_scummy | 2 | 16f38e04-f8b1-40ed-ad01-8da8559ec78e | create_map_object |
| objects | bookshelf | 1 | 5b717d36-1d72-4d8e-83b3-6cf9694bc76f | create_map_object |
| objects | bookshelf | 2 | e1c101b2-55ef-4284-9043-6de75fa4b5ea | create_map_object |
| characters | cast_eccentric_genius_f | 1 | 6172cd82-00ce-46ca-9fd8-ce5540c2b8f8 | create_character |
| characters | cast_woman_lead_older | 1 | 340a796f-93f1-4b8b-97e7-5377e0928c4e | create_character |
| characters | cast_black_woman_young | 1 | 6ee72591-8454-4026-9334-ca0dca82d590 | create_character |
| characters | cast_wheelchair_user | 1 | 1abce614-7a5f-4a1c-ac28-9f9a70a7d683 | create_character |
| cosmetics | hat_medium | 1 | 8bcc1df4-af77-42fb-aca9-0b2ed00c0018 | create_map_object |
| cosmetics | hat_medium | 2 | 3d3b735b-a825-4782-aa34-d1b119f1fe46 | create_map_object |
| cosmetics | hat_sports | 1 | 4ec67b61-d96c-44dd-acb0-acb89f5864dc | create_map_object |
| cosmetics | hat_sports | 2 | b12e9727-0cc5-44a2-9743-41c7869f9774 | create_map_object |
| cosmetics | lab_coat | 1 | 358ebc6e-55fc-46e6-b27e-6b15dd852518 | create_map_object |
| cosmetics | lab_coat | 2 | f381f1fa-eb8a-47fc-bb4d-e349c4911e79 | create_map_object |

Deferred (per rulings, not pixellab jobs): icons (gpt-image-1 pipeline + doom-icon
direction now needs a fresh ruling), UI chrome (author in-engine / create_ui_asset).
See REROLL_RUN_2026-07-21.md "Needs approach ruling".
