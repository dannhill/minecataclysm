# UX-05 — Native recipe shortcuts

K exposes All, Favorites, Recent and Unfinished. CDDA resolves the opening view:
reachable unfinished work first, otherwise currently known recent recipes,
otherwise known favorites, otherwise All. An explicit tab stays active until
another choice or the next opening. Search and batches apply within the native
scope. Filtering happens before the 256-row limit, so large catalogs do not
hide favorites/history. Recent uses CDDA's unique last-20 started recipes,
newest first, including matching unfinished work. It is not a completion counter.

Favorites reuse uistate.favorite_recipes and read_recipes. The native command
binds the catalog/view entry, revalidates present knowledge/book/helper access,
checks expected favorite state, and sets an explicit desired value. It runs as
UI metadata during pause/activities, without starting work or charging moves.
The ordinary command ledger rejects expired/conflicting requests and replays a
cached result for an exact duplicate. The client never flips its own copy or
closes K; it waits for result/state and refreshes the authoritative catalog.
Reconnect/close discard transient handles. Both preference/history collections
already live in native world uistate.json, shared by its characters; no new
character save field or client persistence is introduced.

Recipe favorites are separate from favorite physical components. The existing
no_favorite/no_equipped ingredient protection and native sources/confirmation/
ACT_CRAFT remain. A missing-material/light reason stays visible in shortcuts;
being a favorite or recent never implies craftability. Resume tests check the
remaining requirements directly, without recognizing errors by Italian labels.

The new metadata test found weighted-list selection burning RNG for empty item
variant sets. item::select_itype_variant now returns immediately in that case.
Nonempty variant selection is unchanged. This intentionally changes subsequent
random-stream order by eliminating meaningless draws, without introducing new
probabilities or gameplay authority. Validate crafting/read-only metadata and
native item/reload behavior, retain the original failing evidence.

A future Frequent view needs completion-event accounting, correct batch/result
semantics and persistence; it must not pretend native started history counts
completed jobs. Subrecipe links, additional result phases/byproducts/practice,
body-first medicine, rig/UV/animation/audio and full SAVE-001 remain separate.
