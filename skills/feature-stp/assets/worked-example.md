# Worked example - captions on demand (fictional)

Copy the shape, not the cases. The product and the feature are invented.

## The feature

A team photo library adds "captions on demand": a person opens a photo and asks
for a caption; the caption is generated once and then shown to everyone in the
organization who can open that photo. An organization admin can switch the
feature on or off.

- Product spec: captions in English, Spanish and German, plus a mood label.
- Design: this release ships English and Spanish only, no mood label, and the
  switch only hides the button - it does not generate captions for photos
  already in the library.

## What went wrong first

A forty-case draft was written from the backend contract. Titles named request
fields. Cases checked the stream protocol, caption length limits and storage
keys. German and the mood label got their own cases although the build did not
ship them. The requirement cells were rewritten as "two languages, button
hidden by default", so the plan no longer said what the product promised.

## What good looked like

**Layer 1 kept the product wording.** German and the mood label stayed on their
requirement rows, marked "not in this release".

**Layer 2 carried the build.** D1 English and Spanish only; D2 no mood label;
D3 the switch hides the button and starts nothing; D4 one caption per photo per
organization; D5 people's names in a caption are not translated.

**Six cases**, the combinations as a matrix inside the first one:

| Case | Protects |
|---|---|
| TC-01 Ask for a caption on every photo type, in English and in Spanish | The caption appears; the photo is unchanged |
| TC-02 Admin switches captions off, then on again | The button disappears and returns |
| TC-03 A second person opens a photo already captioned | Shown at once, no second wait |
| TC-04 Photos already in the library stay uncaptioned until someone asks | Switching on is not a backfill |
| TC-05 A person who cannot open a photo cannot read its caption | The block covers what is made from the photo |
| TC-06 Nobody reads another organization's captions | A caption belongs to the organization that asked |

**Cuts with a why:** German and the mood label are not in this release; the
stream, length limits and storage keys are developer tests.

## The lesson: one cut came back

TC-05 and TC-06 were first cut as "access is one rule, already tested
elsewhere". A sibling feature then broke exactly there: people could read text
generated from a document they were not allowed to open. Generated text is
fetched by its own request, so it is allowed or refused on its own - and can be
missed on its own. When you cut a requirement because something else covers it,
name the request that would have to be wrong for you to be wrong.

## False-failure guard

People's names inside a caption may stay in the original language (D5). The
expected result of TC-01 says so, so a tester does not mark it as a failure.
