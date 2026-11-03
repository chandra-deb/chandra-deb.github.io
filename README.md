# chandra-deb.github.io

A minimal personal blog, built with Jekyll and published automatically by GitHub Pages.

**Live site:** <https://chandra-deb.github.io>

## How it works

- Write posts as Markdown files in `_posts/`.
- Commit and push to `main`.
- GitHub Pages builds the site and publishes it. There is no separate deploy command.

Everything else is intentionally small: a typography-first layout, tags, RSS, a sitemap, and SEO metadata. The design follows the visitor's light or dark system preference.

## Publish a post

1. Create a file named `_posts/YYYY-MM-DD-your-slug.md`.
2. Start it with front matter:

   ```yaml
   ---
   layout: post
   title: "A clear, specific title"
   description: "One sentence for search results and link previews."
   tags:
     - notes
     - code
   ---
   ```

3. Write the post in Markdown, below the second `---`.
4. Commit and push:

   ```sh
   git add .
   git commit -m "post: add a clear, specific title"
   git push
   ```

GitHub Pages usually rebuilds within a minute. The post will be at `https://chandra-deb.github.io/your-slug/`.

Read [WRITING.md](WRITING.md) for the full house rules: filenames, tags, images, drafts, and a pre-publish checklist.

## GitHub Pages settings

GitHub Pages is already enabled for this repository:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/ (root)`
- **URL:** <https://chandra-deb.github.io>

If those settings ever change, restore them under **Settings → Pages**.

### Custom domain (optional)

The blog intentionally has no `CNAME` file right now. A previous `CNAME` for `nuistcams.me` was removed because that domain's DNS points to another server, not GitHub Pages; the Pages build for that commit failed. The domain currently serves a different app, so use a subdomain if you want to keep that app online. The blog is served from the GitHub Pages URL instead.

To move the blog to a custom domain later:

1. Point the domain's DNS at GitHub Pages:
   - Apex domain: GitHub's A records (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`).
   - Subdomain: a `CNAME` record pointing to `chandra-deb.github.io`.
2. Add the domain in **Settings → Pages → Custom domain** and save.
3. Wait for DNS to propagate and for GitHub to issue the certificate.
4. Change `url` in `_config.yml` to the new domain.

Do not commit a new `CNAME` file until the DNS is ready. If the domain already hosts another site, use a subdomain such as `blog.example.com` rather than taking over the apex.

## Repository layout

```text
_config.yml            Site title, description, author, URL, plugins
_posts/                Published posts (Markdown)
_drafts/               Unpublished drafts (never published by GitHub Pages)
_layouts/              Page, post, and base layouts
_includes/             Header, footer, and <head>
index.html             Home page (list of posts)
tags.html              Tag index and filtering
about.md               About page
404.html               Not-found page
assets/css/site.css    All styles
assets/js/tags.js      Tag filtering
assets/images/         Post images
WRITING.md             House rules for writing and publishing
```

## Customize

- **Site title, description, author, URL, timezone:** `_config.yml`
- **About page:** `about.md`
- **Colors and typography:** the variables at the top of `assets/css/site.css`
- **Navigation:** `_includes/header.html`
- **Footer:** `_includes/footer.html`
- **Home page intro:** `index.html` and `description` in `_config.yml`

## Local preview (optional)

Writing and pushing is enough. If you want to preview locally, install Ruby and Bundler, then:

```sh
bundle install
bundle exec jekyll serve --livereload --drafts
```

Open <http://localhost:4000>.

## Troubleshooting

- **A post is missing:** confirm the file is in `_posts/`, follows `YYYY-MM-DD-slug.md`, has valid YAML front matter, and is not dated in the future.
- **A post has no tags:** tags must be a YAML list under `tags:`, one per line, prefixed with `-`.
- **Tag filtering does nothing:** the tags page needs JavaScript. Also check that the tag uses lowercase letters, numbers, and hyphens only.
- **The build failed:** open the **Actions** tab on GitHub and read the Pages build log. A YAML typo in front matter is the usual cause.
- **The site is not updating:** wait for the Pages build to finish, then hard-refresh the page.

## House rules

See [WRITING.md](WRITING.md).
