# Adding the Lost Collective TOV Model to Claude Code

## Step 1: Copy the file into your repo

Open Terminal and run:

```bash
cp ~/Downloads/lost-collective-tone-of-voice.md /Users/brettpatman/shopify-themes/lost-collective/docs/lost-collective-tov.md
```

This assumes the file downloaded to your Downloads folder. If it went somewhere else, adjust the first path.

The `docs/` folder may not exist yet. If you get an error, run this first:

```bash
mkdir -p /Users/brettpatman/shopify-themes/lost-collective/docs
```

Then run the copy command again.


## Step 2: Reference it in CLAUDE.md

Open your CLAUDE.md file. If you don't have one yet, create it at the root of your repo:

```
/Users/brettpatman/shopify-themes/lost-collective/CLAUDE.md
```

Add the following block to CLAUDE.md (at the top or in a prominent position):

```markdown
## Tone of Voice

All content generated for Lost Collective (collection descriptions, product descriptions, blog posts, social media captions, ad copy, website copy) MUST follow the tone of voice model defined in:

**docs/lost-collective-tov.md**

Read this file before generating any content. It contains:
- Core voice traits and rules
- Banned words and phrases (AI slop list)
- Calibration examples from Brett's published writing
- Content structure patterns for different formats
- A checklist to test content before publishing

Key rules:
- Website/Shopify content is always about the place, never about Brett (except the About page)
- First person (I) for social media and blog posts where personal perspective is appropriate
- Historical facts are essential, not optional
- Sensory, visceral writing — make people imagine being there
- No em dashes, no hashtags on Facebook, no generic emotional language
```


## Step 3: Verify it works

Open Claude Code in your project directory and ask it something like:

```
Write a collection description for Wangi Power Station
```

If it's loaded correctly, the output should follow the TOV rules — specific, historically grounded, no AI slop, no first person, focused on the place and the people who worked there.

If it produces generic copy like "explore the haunting beauty of this industrial relic," the file isn't being read. Check that the path in CLAUDE.md matches where you actually put the file.


## That's it

The TOV model will now be available to Claude Code for any content generation task. You can prompt it to write collection descriptions, product copy, social captions, blog drafts, or ad copy, and it will follow your voice.
