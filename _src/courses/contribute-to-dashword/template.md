---
title: Template
desc: Articles on our site are written in Markdown. However, since most people are not familiar with this format of writing, we've created a Google Docs template you can use.
pageSlug: template
num: 4
---

Articles on our site are written in Markdown. However, since most people are not familiar with this format of writing, we've created a Google Docs template you can use.

First, [go to our Google Docs template here](https://docs.google.com/document/d/1k1Hd4saP6OZSxWO9WWjhJ33ybQavvWkI2CgN6YPcexo/edit?usp=sharing). Then, make a copy for you to start writing in.

Now, your document must adhere to a strict set of rules in order for it to be accepted by our systems.

# Metadata

Everything at the top of the article between the `---` lines are the article's metadata, documented below.

| Parameter | Required? | Content |
|-|-|-|
| Title | Yes | This will be the title of your article. |
| Desc | Yes | A short description of your article. Usually, repeating the first paragraph here is acceptable, just make sure to remove any links and other styling (like **bold** and *italics*). |
| Cover | Yes | This *must* be a link to an image, *not* a link to the page the image is on. Usually, this means the link ends in the file extension of the image (like `.png`). You can generate a link for an image using [Imgur](https://imgur.com/upload), which doesn't require an account.
| Cover Source | No | This should be a link to the website or post where you got the image from, *but not the image itself*. This isn't needed if the image is by you. |
| Tags | Yes | At least one tag (called "categories" on this site) is needed. You can [find a list of our categories here](/categories/). If your article is part of more than one category, separate categories by commas and a space. Finally, what you should write to reference a specific category should be what it says in the URL for that category's page. For example, for our [2.21 category](/categories/2.2/), you would actually write "2.2" since the URL for that category's page is `/category/2.2/`. |
| Author Key | Yes | If you don't already have an [Author Page](/authors/), then put your desired author username here. This will be shown in the URL for your Author Page (like `/authors/moldy/`). If you already have an Author Page, then include your author key here. This is in the URL for your Author Page (for `/authors/moldy/` your author key would be `moldy`, for example). No uppercase or special characters please! |

The remaining Metadata is only required if you do not have an Author Page. And even then, only an Author Name and Photo is required.

| Parameter | Required | Content |
|-|-|-|
| Author Name | Yes | Your display name on this site. It can feature capital letters and spaces. |
| Author Photo | Yes | Like the article cover, this *must* be a link to an image, *not* a link to the page the image is on. This will be your Author Page avatar. Again, you can use [Imgur](https://imgur.com/upload) to get a link. Author Photos cannot be GIFs. |
| Author Bio | No | A short, 1-2 sentence bio for your Author Page. |
| Author YouTube | No | Your YouTube channel handle. |
| Author Twitter | No | Your Twitter profile handle. |
| Author Twitch | No | Your Twitch channel username. |
| Author Discord | No | An invite code to a Discord server. Not the entire link, just everything after the `.gg/` portion. |
| Author GDBrowser | No | Your in-game Geometry Dash account username. |

For any parameters not required, you can simply remove it. For example, if you already have an Author Page and you don't need to provide a Cover Source, your metadata can just look like:

```
---
Title: Article Title
Desc: A short description about the article shown on our website. Usually repeating the first paragraph here is enough, just make sure to remove any links or styling.
Cover: https://i.imgur.com/example.png
Tags: demonlist, news
Author Key: moldy
---
```

# Article Body

Everything after the second `---` line is the actual content of your article. Please separate all paragraphs, headings, lists, images, tables, and horizontal lines with a blank line.

Use standard Google Docs headings, lists, images, tables, and horizontal lines. Do not simply give a paragraph a bigger font size and expect us to treat it as a heading.

## Headings

To use headings, press the **Normal Text** drop down and select either **Heading 1**, **Heading 2**, or **Heading 3**.

Headings must be used in a proper order. For example, you cannot use a Heading 2 without an earlier Heading 1 preceding it. *Do not* use headings solely for aesthetic appeal. They should define article sections and subsections.

Most of the time, you will probably only need to use level 1 headings. But if your article is an in depth tutorial or guide, you may want to also use level 2 headings.

## Lists

Use standard Google Docs unordered and ordered lists.

## Images

Unlike the article cover or author photo, you don't need to get an image link for these. Simply press **Insert > Image > Upload from computer** to insert an image. Just make sure, like all other article elements, there are blank lines before and after it.

Also, if the image fits the full width of the page, *do not* scale it to be smaller. *Doing so will hurt the image quality when we upload it to our site!*

## Tables

Press **Insert > Table** to insert a table. The first row will be for the table header, while the rest will be typical table rows.

Don't do anything complex with tables, such as style them or merge cells.

## Horizontal Lines

If you want to insert a horizontal line in your article, press **Insert > Horizontal line**. Again, make sure there are blank lines ahead of and after it.

## Bold, Italics, and Links

Bold, italics, and links can be inserted by selecting the text you want and using the regular Google Docs UI to either bold it, italicize it, or turn it into a link.

## Blockquotes

Google Docs does not have a native blockquotes feature. Instead, any paragraph preceding with a **greater than symbol** (>) and a space will be treated as a blockquote. For example:

```
This will be a regular paragraph.

> This will be a blockquote.
```

---

The provided Google Docs template has examples of all the article elements you can use, so if in doubt, use that as a reference. Do not add custom styles to anything, as this will throw off our systems.

Once you've written your article, you can press **Next** below to learn how to [submit it for publication](/courses/contribute-to-dashword/submission/).
