# Lost Collective — Klaviyo Flow Email Copy

All copy follows the Lost Collective tone of voice: place-focused, historically grounded,
sensory, no em dashes, no AI slop, Australian spelling. Short sentences.

Paste each email's subject line, preview text, and body into the corresponding Klaviyo
flow message via the visual editor. Replace all existing placeholder text.

---

## HOW TO EDIT IN KLAVIYO

1. Open Klaviyo > Flows
2. Click the flow name
3. Click the email block you want to edit
4. Click "Edit" on the email
5. Update Subject Line and Preview Text in the settings panel
6. In the email body: click each text block and replace with the copy below
7. Save and close

---

## 1. WELCOME SERIES — NEW SUBSCRIBER
*Trigger: Added to Email List (new subscriber, no previous purchase)*

---

### Email 1 — "The places that got left behind"

**Subject:** The places that got left behind
**Preview:** What you will find here, and why these places matter.

**Body:**

Hey {% if person.first_name %}{{ person.first_name }}{% else %}there{% endif %},

Thanks for being here. I'm Brett, the photographer behind Lost Collective.

A few years ago I posted a photograph of Wangi Power Station on Facebook. Nothing
special, just an old building I'd spent a day shooting on Lake Macquarie. What
happened next surprised me. Former workers started appearing in the comments. Their
families. People who'd grown up in the shadow of the cooling towers. One man's father
had worked there for thirty years. He said he'd never seen the inside photographed like
that.

That's what Lost Collective is really about.

These aren't just abandoned buildings. They're places where people worked, were born,
were treated, made things. The photographs exist because the people did.

Over the next couple of weeks I'll share some of those stories with you, the places,
how I found them, what they felt like to walk through, and how the prints are made.

For now, browse the collections.

Brett

---

### Email 2 — "What it feels like inside a place that's been forgotten"

**Subject:** What it feels like inside a place that's been forgotten
**Preview:** The light. The silence. What a camera picks up that most people miss.

**Body:**

The first thing you notice inside a derelict power station is the light.

It comes through broken windows, through gaps in the roof, through vent shafts that
haven't opened in decades. It lands on turbines the size of houses. It catches the
dust. It does things that are impossible to replicate anywhere else.

This is what I photograph.

Not the building as a historical record, you can find that in municipal archives and
local history societies. What I'm photographing is this specific quality of light, at
this specific time of day, in this specific state of decay. A year from now it will be
different. A decade from now most of these buildings won't exist in the form I
photographed them.

The photographs exist because the buildings existed. The prints are made to last longer
than either of us.

Browse the current collections.

Brett

---

### Email 3 — "The paper. The size. The care that goes into each print."

**Subject:** The paper. The size. The care that goes into each print.
**Preview:** What you are actually buying when you buy a Lost Collective print.

**Body:**

A lot of photography gets sold as a product. A print. An item that ships in a tube.

That's not how I think about it.

Every photograph in this store started as a RAW file from a camera I carried into a
place most people can't access or wouldn't enter. Some images take years of editing
before they become something I'd put my name on. The tones in an abandoned hospital
corridor at midday are different from the tones in a power station at dawn. Getting
that right takes time.

The prints are made on archival paper. Sizes start at XS and go up to prints large
enough to fill a wall. Framed options ship flat. Unframed options roll. Every print is
made to order.

If you're not sure where to start, the Wangi Power Station and White Bay Power Station
collections are where most people begin. Both are large industrial spaces, both have
strong natural light, both have prints at every size.

If you have questions about which size would work for your space, reply to this email.
I read everything.

Brett

---

### Email 4 — "What others found in these places"

**Subject:** What others found in these places
**Preview:** The collection that surprises people. And what happened to the building after.

**Body:**

Most people who buy from here find one place that pulls them in harder than the others.

For some it's Wangi Power Station, a Lake Macquarie coal plant that operated from 1950
to 1986, now heritage listed and slowly being restored. The turbine hall is one of the
most photographed industrial interiors in Australia.

For others it's the Blayney Abattoir, a regional New South Wales works that processed
livestock for sixty years and closed in the early 2000s. The photographs inside are
harder to look at, and they're the ones people can't stop looking at.

A few people find their way to the Japan series first. Kinugawa Onsen is a resort town
north of Tokyo where the bubble economy left behind a strip of derelict hotels sitting
alongside a functioning town. It's a different kind of abandonment to what you see in
Australia. The scale is different. The light is different.

None of these places are museums. Most are in various states of demolition, development,
or slow deterioration. Some no longer exist in the form I photographed them.

That's why the prints exist.

Browse the full archive.

Brett

---

## 2. WELCOME SERIES — EXISTING CUSTOMER
*Trigger: Added to Email List (has a previous Shopify purchase)*

---

### Email 1 — Existing customer welcome

**Subject:** You've ordered before. Here's what's new.
**Preview:** New series, new places. The work keeps going.

**Body:**

Hey {% if person.first_name %}{{ person.first_name }}{% else %}there{% endif %},

You've bought from here before, which means you already know what these photographs are
about.

Since your last order, new collections have been added to the archive. Hotel Motel 101,
Morwell Power Station, and recent work from the Kinugawa Onsen series in Japan are all
worth a look if you haven't seen them.

If there's a collection you've been watching, or a place you'd like to see photographed,
reply to this email. It's a direct line.

Brett

---

### Email 2 — Social media

**Subject:** Where the new work appears first
**Preview:** Instagram and Facebook, before anything goes to the store.

**Body:**

New photographs appear on Instagram and Facebook before they make it to the store,
sometimes months before.

If you want to see a place as it's being photographed, that's where to look. Work in
progress, behind-the-scenes images, the occasional historical note about a building.
No promotions, no giveaways. Just the places.

Follow on Instagram: @lostc0llective
Follow on Facebook: Lost Collective

Brett

---

## 3. ABANDONED CHECKOUT REMINDER
*Trigger: Started Checkout, did not complete*

---

### Email 1 — 1 hour after abandonment

**Subject:** You left something behind
**Preview:** Your cart is still saved.

**Body:**

You were close.

{{ event.extra.line_items | first | map: attribute="product_title" | first }} is still
in your cart, along with everything else you had saved.

Prints are made to order, so there's no stock count ticking down. But if you had
questions about sizing, framing, or delivery, reply to this email. I'm happy to help.

Complete your order.

Brett

---

### Email 2 — 24 hours after abandonment

**Subject:** The story behind the print you were looking at
**Preview:** Where it was photographed, and what happened to the building.

**Body:**

Every photograph in this store has a history.

A specific building, a specific place, a specific time when that building still existed
in the form you're looking at. By the time I photograph these places, most of the people
who worked there are gone. The machinery is still. The light does things it won't do
anywhere else.

If you'd like to know more about the place in the photograph you were looking at, the
history, what the building was used for, what it looks like now, reply to this email.

Your cart is still saved.

Complete your order.

Brett

---

### Email 3 — 72 hours after abandonment

**Subject:** These prints don't last forever
**Preview:** A note on why some of these don't get restocked.

**Body:**

Lost Collective prints are made to order. But the photographs themselves aren't
permanent fixtures of the store.

When a building gets demolished, or a series gets retired, those prints come down. The
Wangi Power Station series is currently under heritage redevelopment. At some point the
building will be restored, the decay will be gone, and this version of the place will
no longer exist to photograph.

I'm not saying that to pressure you. I'm saying it because it's true.

Your cart has {{ event.extra.line_items | size }} item(s) in it.

Complete your order.

Brett

---

## 4. BROWSE ABANDONMENT
*Trigger: Viewed a product page, did not add to cart or purchase*

---

### Email 1 — 4 hours after browsing

**Subject:** The place you were looking at
**Preview:** A bit more about the history, if you are interested.

**Body:**

You spent some time looking at one of the collections.

Most people who look at these photographs spend a few minutes reading the background,
the building's history, who worked there, what happened to it. If you didn't get to
that, it's on the collection page.

Fine art prints are made to order. They start from $50 and go up to large format. Framed and unframed options available.

If you'd like to know more about any specific collection or photograph, reply to this
email.

Brett

---

### Email 2 — 48 hours after browsing

**Subject:** One more thing about that collection
**Preview:** A detail about sizing that might help you decide.

**Body:**

If you're still deciding on a print, the most common question I get is about size.

The XS prints are the entry point, roughly 20cm by 30cm depending on the image ratio.
Good for a desk or a narrow wall. The larger formats, A1 and above, are for rooms where
you want the photograph to do the work.

If you're not sure what would work for your space, reply to this email with a rough
description of the wall. I've helped a few people get this right and it makes a
difference.

Brett

---

## 5. CUSTOMER THANK YOU
*Trigger: Placed Order*

---

### Email 1 — New customer (first purchase)

**Subject:** Your order is in. Here's what happens next.
**Preview:** How your print is made, and when it ships.

**Body:**

Thank you for your order.

Your print is made specifically for you, not pulled from a shelf. Production takes 3
to 5 business days, then it ships. You'll get a tracking notification when it leaves.

If anything looks wrong with your order, the wrong size, the wrong frame option,
anything, reply to this email now before production starts.

And if you have questions about the print itself, the location, the history of the
building, what it looks like today, I'm happy to talk about it.

Brett

---

### Email 2 — Repeat customer (second or more purchase)

**Subject:** Another one. Thank you.
**Preview:** Your print is in production.

**Body:**

You've ordered before, so you know how this works.

Your print is in production. Three to five business days, then it ships. Tracking
notification on the way.

If there's a collection you've been watching or somewhere you'd like to see work from,
reply to this email. The archive is deep and not everything ends up on the store.

Brett

---

## 6. PRODUCT REVIEW / CROSS SELL
*Trigger: Order Fulfilled (approximately 10-14 days after)*

---

### Email 1

**Subject:** How does the print look on your wall?
**Preview:** A quick question, and a suggestion for what to look at next.

**Body:**

Your print should have arrived by now.

If everything looks right, the size, the colour, the framing, a review would mean a
lot. It takes two minutes and it matters more than most people realise for a small
independent store.

Leave a review.

If something isn't right, a damaged frame, a colour that looks off compared to what you
saw on screen, anything at all, reply to this email. I'll sort it out.

And if you're thinking about what to look at next: if you ordered from the Wangi series,
the White Bay Power Station collection is photographed in the same register. Same
palette, same industrial scale. Worth a look.

Browse related collections.

Brett

---

## 7. CUSTOMER WINBACK
*Trigger: Last purchase was 90+ days ago, no recent activity*

---

### Email 1 — First contact

**Subject:** It's been a while
**Preview:** New work has been added since your last order.

**Body:**

It's been a while since your last order.

A few new collections have been added since then. Hotel Motel 101, Morwell Power
Station, work from the Kinugawa Onsen series in Japan. The archive keeps growing.

If you're curious what's changed, browse what's new.

Brett

---

### Email 2 — 21 days after Email 1

**Subject:** A photograph you might not have seen
**Preview:** From the Japan series. A different kind of place.

**Body:**

If you've mostly looked at the Australian industrial series, the power stations, the
abattoir, the hospitals, the Japan work might surprise you.

Kinugawa Onsen is a resort town north of Tokyo. The bubble economy built it up through
the 1970s and 1980s, then left it behind when the money went. What remains is a strip
of enormous derelict hotels sitting alongside a functioning town, in various states of
slow collapse.

It's a different kind of abandonment to what you see in Australia. The scale is
different. The light is different. The history is different.

See the Japan collections.

Brett

---

### Email 3 — 30 days after Email 2

**Subject:** One last thing before I go quiet
**Preview:** If nothing here is right for you right now, that is OK. But read this first.

**Body:**

This is the last email I'll send for a while.

If nothing in the store is right for you right now, the wrong style, the wrong size,
the wrong budget, that's fine. You can stay on the list and hear from me less often,
or unsubscribe below and come back when you're ready.

But if there's a place you've always wanted to see photographed, or a building type
that interests you, reply to this email and tell me. I'm always looking for the next
place to shoot.

Brett

---

## 8. SUNSET — RE-PERMISSION FLOW
*Trigger: Subscriber has not opened or clicked for 180+ days*

---

### Email 1 — Re-engagement check

**Subject:** Are you still interested?
**Preview:** It's been a while since you've opened anything from us.

**Body:**

Hi {% if person.first_name %}{{ person.first_name }}{% else %}there{% endif %},

You haven't opened an email from Lost Collective in a while.

That's fine. Inboxes get busy, things get buried. But I don't want to keep sending
emails to people who aren't interested.

If you'd like to stay on the list, click the button below. If not, you don't need to
do anything. I'll remove you automatically in a few days.

Yes, keep me on the list.

Brett

---

### Email 2 — Final contact

**Subject:** Last chance to stay on the list
**Preview:** After this, I'll stop emailing.

**Body:**

This is the last email you'll receive from Lost Collective unless you opt back in.

If you'd like to stay connected, new collections, occasional notes from the places,
click below. Otherwise, I hope the photographs meant something to you at some point.

Keep me subscribed.

Brett

---

## SUBJECT LINE SUMMARY TABLE
*Quick reference for updating subjects and preview texts in Klaviyo*

| Flow | Email | Current Subject (needs changing) | New Subject | Preview Text |
|---|---|---|---|---|
| Welcome New | 1 | The places that got left behind | The places that got left behind | What you will find here, and why these places matter. |
| Welcome New | 2 | What it feels like inside a place that's been forgotten | What it feels like inside a place that's been forgotten | The light. The silence. What a camera picks up that most people miss. |
| Welcome New | 3 | The paper. The size. The care that goes into each print. | The paper. The size. The care that goes into each print. | What you are actually buying when you buy a Lost Collective print. |
| Welcome New | 4 | What others found in these places | What others found in these places | The collection that surprises people. And what happened to the building after. |
| Welcome Existing | 1 | **Thanks for subscribing!** | You've ordered before. Here's what's new. | New series, new places. The work keeps going. |
| Welcome Existing | 2 | **Follow us on social media!** | Where the new work appears first | Instagram and Facebook, before anything goes to the store. |
| Abandoned Checkout | 1 | You left something behind | You left something behind | Your cart is still saved. |
| Abandoned Checkout | 2 | The story behind the print you were looking at | The story behind the print you were looking at | Where it was photographed, and what happened to the building. |
| Abandoned Checkout | 3 | These prints don't last forever | These prints don't last forever | A note on why some of these don't get restocked. |
| Browse Abandonment | 1 | **Did you see something you liked?** | The place you were looking at | A bit more about the history, if you are interested. |
| Browse Abandonment | 2 | Still thinking it over? | One more thing about that collection | A detail about sizing that might help you decide. |
| Thank You | New | **You're what makes us great** | Your order is in. Here's what happens next. | How your print is made, and when it ships. |
| Thank You | Repeat | **Wow, thank you again!** | Another one. Thank you. | Your print is in production. |
| Review / Cross Sell | 1 | **Don't keep it to yourself!** | How does the print look on your wall? | A quick question, and a suggestion for what to look at next. |
| Winback | 1 | It's been a while... | It's been a while | New work has been added since your last order. |
| Winback | 2 | We've missed you. | A photograph you might not have seen | From the Japan series. A different kind of place. |
| Winback | 3 | One last thing before I go quiet | One last thing before I go quiet | If nothing here is right for you right now, that is OK. But read this first. |
| Sunset | 1 | Time to say goodbye? | Are you still interested? | It's been a while since you've opened anything from us. |
| Sunset | 2 | This is the last email you'll ever see... | Last chance to stay on the list | After this, I'll stop emailing. |

*Bold = poor subject line that must be changed before going live.*
