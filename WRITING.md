# Writing rules

These are the house rules for this blog. They exist so that publishing stays a three-step job: **write, commit, push**. GitHub Pages does the rest.

If a rule here is wrong for you, change this file first, then change the site. Do not leave the rules and the site out of sync.

## 1. One post, one file

- Published posts live in `_posts/`.
- The filename **must** be `YYYY-MM-DD-slug.md`.
- The date in the filename is the publish date. Dates are interpreted in the site timezone, currently `Asia/Shanghai` in `_config.yml`.
- The slug becomes the post URL: `_posts/2026-11-03-my-first-post.md` → `/my-first-post/`.
- Slugs must be unique. Two posts with the same slug will overwrite each other.
- Slug rules: lowercase `a-z`, digits `0-9`, and hyphens only. No spaces, underscores, capital letters, or leading/trailing hyphens. Example: `setting-up-a-home-server`.
- The following slugs are reserved and must not be used for posts: `about`, `tags`, `404`, `feed`, `sitemap`, `robots`, `assets`.
- Do not rename the file after publishing unless you accept that the old URL will break. The URL is derived from the filename.

Examples:

```text
_posts/2026-11-03-hello-world.md          ✅
_posts/2026-11-03-Hello-World.md          ❌ capital letters
_posts/2026-11-03_hello_world.md          ❌ underscores
_posts/03-11-2026-hello-world.md          ❌ wrong date order
_posts/2026-11-03-hello-world.markdown    ❌ use .md
```

## 2. Front matter is mandatory

Every post starts and ends its front matter with `---`. Required fields:

```yaml
---
layout: post
title: "A clear, specific title"
tags:
  - notes
  - code
---
```

Optional fields:

```yaml
description: "One sentence for search results and link previews."
published: false
```

Rules:

- `layout` must be `post`.
- `title` must be present and wrapped in double quotes. Quoting avoids YAML errors when the title contains `:`, `#`, or other punctuation.
- `description` is optional but recommended. Keep it to one sentence, under about 160 characters. It appears in search results, RSS, and link previews.
- You normally do not need a `date:` field; the filename supplies the date. Only add `date: 2026-11-03 14:30:00 +0000` if you need a specific publication time, and remember that it overrides the filename.
- Do not use a future date as a draft. Future-dated posts are hidden until that date passes; use `_drafts/` instead.
- Front matter must be valid YAML. Indentation matters: two spaces per level, no tabs.

## 3. Tags

Tags are how the blog is organized. Keep the vocabulary small and consistent.

- Use **1 to 5 tags** per post.
- Tags are lowercase and hyphen-separated: `web-dev`, `book-notes`, `linux`.
- No `#`, no spaces, no capital letters, no trailing punctuation: use `cooking` not `#Cooking`.
- Prefer an existing tag over a new synonym. Check the [tags page](https://chandra-deb.github.io/tags/) before inventing one.
- Pick the singular or plural form once and keep it. For example, use `book` everywhere, not `book` in one post and `books` in another.
- Do not use broad junk tags such as `blog`, `post`, `misc`, or `other`. If a post fits nowhere, a single honest tag is better than five vague ones.
- A tag that is used by zero posts will not appear on the tags page.
- Tags are written as a YAML list, one per line. Do not use inline `[tag1, tag2]` syntax; the list form is easier to read and less error-prone.

Examples:

```yaml
tags:
  - linux
  - self-hosting
```

```yaml
tags:
  - reading
```

The starter tags `meta` and `guide` come from the sample post. Delete them from the vocabulary when you delete that post.

## 4. Markdown rules

The post title is already the page's `H1`. Do not repeat it in the body and do not add another `#` heading.

- Start body headings at `##`, then `###`.
- Keep one main idea per post. Long posts are fine; unrelated ideas should be separate posts.
- Use fenced code blocks with a language label:

  ````markdown
  ```python
  print("hello")
  ```
  ````

- Use inline code for filenames, commands, and short identifiers: `` `_config.yml` ``.
- Use descriptive link text: `[the Jekyll docs](https://jekyllrb.com/)`, not `[click here](https://jekyllrb.com/)`.
- Internal links use absolute site paths with a trailing slash: `[tags](/tags/)`, `[about](/about/)`.
- External links must include `https://`.
- Blockquotes, tables, footnotes, and task lists are supported by kramdown. Use them when they help; do not decorate for the sake of decoration.
- Raw HTML is allowed only for small structural needs. Never add `<script>`, `<style>`, `<iframe>`, or tracking code to a post.
- Do not paste secrets, API keys, private URLs, or other people's personal information. Once pushed, assume it is public forever.

## 5. Images and files

- Put post images in `assets/images/<post-slug>/`.
- Reference them with an absolute path: `/assets/images/<post-slug>/diagram.png`.
- Always write alt text: `![Diagram of the network layout](/assets/images/my-post/diagram.png)`.
- Compress images before committing. Prefer WebP or JPEG for photos, PNG for screenshots. Keep files under about 500 KB and width under about 1600 px unless there is a real reason not to.
- Do not upload huge original photos or videos. GitHub Pages is not a media host.
- Name files with lowercase letters, digits, and hyphens: `network-layout.webp`.

Example:

```markdown
![The server rack after wiring](/assets/images/home-server/rack.jpg)
```

## 6. Drafts

Use `_drafts/` for unfinished writing. Drafts are never published by GitHub Pages.

- Draft filename: `_drafts/my-unfinished-post.md` (no date prefix).
- Preview drafts locally with `bundle exec jekyll serve --drafts`.
- When the draft is ready, move it to `_posts/`, add the date prefix, and add the required front matter.
- Do not use a future date in `_posts/` as a drafting mechanism. Future posts are not built, but they are easy to forget and can go live unexpectedly when the date passes. Use `_drafts/` instead.

## 7. Publishing checklist

Before every push:

- [ ] File is in `_posts/` and named `YYYY-MM-DD-slug.md`.
- [ ] `layout: post` is present.
- [ ] `title` is present, quoted, and reads well.
- [ ] `description` is present and useful (recommended).
- [ ] There are 1–5 tags, all lowercase and hyphen-separated.
- [ ] Body headings start at `##`.
- [ ] Code fences have a language label.
- [ ] Images have alt text and reasonable file sizes.
- [ ] Internal links start with `/`; external links use `https://`.
- [ ] Front matter is valid YAML.
- [ ] The date is today or earlier.
- [ ] No secrets or private information.

Then:

```sh
git add .
git commit -m "post: add <short description>"
git push
```

Wait for the Pages build to finish, then open the live URL and check the post, its tags, and the home page.

## 8. Editing and deleting posts

- To edit a post, change the same file. Keep the filename and slug unchanged so the URL stays stable.
- Do not "refresh" an old post by changing its filename date. That changes its URL and breaks every existing link.
- To unpublish temporarily, add `published: false` to the front matter. The file stays in the repository but is not built.
- To delete a post, delete the file and push. Its URL will return 404. There are no automatic redirects.
- If a post's slug must change, search the repository for the old URL and update the links in the same commit.

## 9. Things not to touch

- Do not edit `_site/`. It is generated output and is not committed.
- Do not add a `CNAME` file or configure a custom domain until its DNS points at GitHub Pages. A mismatched domain makes the Pages build fail, and the blog silently stays on the old build.
- Do not change `permalink` in `_config.yml` without a plan for existing URLs.
- Do not add Jekyll plugins that GitHub Pages does not support. GitHub Pages builds this site in safe mode with a fixed plugin set.
- Do not commit `vendor/`, `.bundle/`, or local build output.
- Do not put drafts or private notes in `_posts/` and rely on a future date to hide them.

## 10. Commit messages

Not mandatory, but recommended so the history stays readable:

```text
post: add my first post
post: update my first post
site: adjust spacing on tags page
docs: clarify image rules
```

One post per commit is ideal. Avoid mixing a new post with unrelated layout changes.

## 11. If something breaks

1. Open the repository's **Actions** tab and read the Pages build log.
2. Most failures are YAML mistakes in front matter. Check indentation, quotes, and the closing `---`.
3. Fix the file, commit, and push again. The previous live version stays online until a new build succeeds.
4. If the post is missing but the build passed, check the date is not in the future and the filename is correct.

The goal is simple: a post should be a Markdown file, a commit, and a push — nothing else.
