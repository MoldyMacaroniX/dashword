const { DateTime } = require("luxon");
const { execSync } = require('child_process');
const markdownIt = require("markdown-it");
const md = new markdownIt({ html: true, breaks: false });
const markdownItAnchor = require("markdown-it-anchor");
const markdownItImageFigures = require("markdown-it-image-figures");
const cheerio = require('cheerio');
const fs = require("node:fs");
const path = require("node:path");
const pluginRss = require("@11ty/eleventy-plugin-rss").default;

module.exports = function (eleventyConfig) {
    const POSTS_PER_PAGE = 10;

    eleventyConfig.addPlugin(pluginRss);

    /** ======================================
    *   MARKDOWN SETTINGS
    *   ====================================== */

    const mdOptions = {
        html: true, // Allow HTML tags inside markdown
        breaks: true, // Convert '\n' in paragraphs into <br>
        linkify: true, // Autoconvert URL-like text to links
    };

    const markdownLibrary = markdownIt(mdOptions).use(markdownItAnchor, {
        permalink: true, // Makes the heading itself a link
        level: [1, 2, 3, 4], // Apply anchors only to h2, h3, and h4
        permalinkClass: 'header-anchor',
        permalinkSymbol: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M18.3638 15.5355L16.9496 14.1213L18.3638 12.7071C20.3164 10.7545 20.3164 7.58866 18.3638 5.63604C16.4112 3.68341 13.2453 3.68341 11.2927 5.63604L9.87849 7.05025L8.46428 5.63604L9.87849 4.22182C12.6122 1.48815 17.0443 1.48815 19.778 4.22182C22.5117 6.95549 22.5117 11.3876 19.778 14.1213L18.3638 15.5355ZM15.5353 18.364L14.1211 19.7782C11.3875 22.5118 6.95531 22.5118 4.22164 19.7782C1.48797 17.0445 1.48797 12.6123 4.22164 9.87868L5.63585 8.46446L7.05007 9.87868L5.63585 11.2929C3.68323 13.2455 3.68323 16.4113 5.63585 18.364C7.58847 20.3166 10.7543 20.3166 12.7069 18.364L14.1211 16.9497L15.5353 18.364ZM14.8282 7.75736L16.2425 9.17157L9.17139 16.2426L7.75717 14.8284L14.8282 7.75736Z"></path></svg>',
        permalinkBefore: true
    }).use(markdownItImageFigures, {
        figcaption: true, // Enable figure captions from image title attributes
        copyAttrs: true,  // Copy image attributes to the figure element
    });

    // Tell Eleventy to use the customized library for rendering markdown
    eleventyConfig.setLibrary("md", markdownLibrary);

    /** ======================================
    *   INSERT ADS AND OTHER ELEMENTS
    *   ====================================== */

    eleventyConfig.addTransform("insert-ads", function(content) {
        // Only process HTML files
        if (this.page.outputPath && this.page.outputPath.endsWith(".html")) {
            const $ = cheerio.load(content);
            const $pTags = $('.article > p');
            const totalParagraphs = $pTags.length;

            // Define your ad code template literal
            const adPath = path.join(__dirname, "./_src/_includes/ads/post.html");
            const adCode = fs.readFileSync(adPath, "utf8");;

            // Loop through paragraphs (1-indexed for the math)
            $pTags.each((index, element) => {
                const paragraphNumber = index + 1;

                // Check if it's a multiple of 3 and NOT the final paragraph
                if (paragraphNumber % 3 === 0 && paragraphNumber < (totalParagraphs)) {
                    $(element).after(adCode);
                }
            });

            return $.html();
        }

        return content;
    });

    eleventyConfig.addTransform("wrap-tables", function(content) {
        // Only process HTML files
        if (this.page.outputPath && this.page.outputPath.endsWith(".html")) {
            const $ = cheerio.load(content);
            
            // Find all tables and wrap them
            $('table').each(function() {
                $(this).wrap('<div class="table-wrapper"></div>');
            });
            
            return $.html();
        }
        
        return content;
    });
    
    /** ======================================
    *   FOLDERS TO PASSTHROUGH
    *   ====================================== */

    eleventyConfig.addPassthroughCopy('_src/assets');
    eleventyConfig.addPassthroughCopy('_src/_data');
    eleventyConfig.addPassthroughCopy({'_src/static': '.'});

    /** ======================================
    *   COLLECTIONS
    *   ====================================== */

    // Collection: Posts in 'posts' folder
    eleventyConfig.addCollection("posts", (collectionApi) => {
        return collectionApi.getFilteredByGlob("_src/posts/*.md").sort((a, b) => b.date - a.date);
    });

    // Collection: Quizzes in 'quizzes' folder
    eleventyConfig.addCollection("quizzes", function(collection) {
        return collection.getFilteredByGlob("_src/quizzes/*.md").reverse();
    });

    // Collection: Podcast in 'podcast' folder
    eleventyConfig.addCollection("podcast", function(collection) {
        return collection.getFilteredByGlob("_src/podcast/*.md").reverse();
    });

    // Collection: Courses in 'courses' folder
    eleventyConfig.addCollection("courses", function(collectionApi) {
        // Get all markdown files in your target directory
        return collectionApi.getFilteredByGlob("_src/courses/**/*.md").filter(item => {
            // Check if frontmatter property `num` is strictly equal to 1
            return item.data.num === 1;
        }).sort((a, b) => b.date - a.date);
    });

    // Collection: Chunked Tag Pages [/tags/:tag/:page]
    eleventyConfig.addCollection("tagPages", (collectionApi) => {
        const posts = collectionApi.getFilteredByGlob("_src/posts/*.md").sort((a, b) => b.date - a.date);
        const tagMap = {};

        posts.forEach((post) => {
        (post.data.tags || []).forEach((tag) => {
            if (!tagMap[tag]) tagMap[tag] = [];
            tagMap[tag].push(post);
        });
        });

        const tagPages = [];
        Object.keys(tagMap).forEach((tag) => {
        const tagPosts = tagMap[tag];
        const totalPages = Math.ceil(tagPosts.length / POSTS_PER_PAGE);

        for (let i = 0; i < totalPages; i++) {
            tagPages.push({
            tag,
            pageNum: i + 1,
            totalPages,
            posts: tagPosts.slice(i * POSTS_PER_PAGE, (i + 1) * POSTS_PER_PAGE),
            });
        }
        });

        return tagPages;
    });

    // Collection: Chunked Author Pages [/authors/:author/:page]
    eleventyConfig.addCollection("authorPages", (collectionApi) => {
        const courses = collectionApi.getFilteredByGlob("_src/courses/**/*.md").filter(item => {
            // Check if frontmatter property `num` is strictly equal to 1
            return item.data.num === 1;
        });
        let posts = collectionApi.getFilteredByGlob(["_src/posts/*.md", "_src/quizzes/*.md", "_src/podcast/*.md"]).sort((a, b) => b.date - a.date);
        posts = [...posts, ...courses];
        posts = posts.sort((a, b) => b.date - a.date);
        const authorMap = {};

        posts.forEach((post) => {
        const author = post.data.author;
        if (author) {
            if (!authorMap[author]) authorMap[author] = [];
            authorMap[author].push(post);
        }
        });

        const authorPages = [];
        Object.keys(authorMap).forEach((author) => {
        const authorPosts = authorMap[author];
        const totalPages = Math.ceil(authorPosts.length / POSTS_PER_PAGE);

        for (let i = 0; i < totalPages; i++) {
            authorPages.push({
            authorKey: author,
            pageNum: i + 1,
            totalPages,
            posts: authorPosts.slice(i * POSTS_PER_PAGE, (i + 1) * POSTS_PER_PAGE),
            });
        }
        });

        return authorPages;
    });

    /** ======================================
    *   FILTERS
    *   ====================================== */

    // Filter: Fetch Author Data from authors.json
    eleventyConfig.addFilter("getAuthor", (authorKey, authorsData) => {
        if (!authorKey || !authorsData) return { name: authorKey };
        return authorsData.find((a) => a.key === authorKey) || { key: authorKey, name: authorKey };
    });

    // Filter: Fetch Tag Data from tagInfo.json (with fallback if missing)
    eleventyConfig.addFilter("getTagInfo", (tagKey, tagsData) => {
        const fallback = { key: tagKey, name: tagKey };
        if (!tagKey || !tagsData) return fallback;
        return tagsData.find((t) => t.key === tagKey) || fallback;
    });

    eleventyConfig.addFilter("date", dateObj => {
        if (dateObj instanceof Date) {
            return DateTime.fromJSDate(dateObj, { zone: "utc" }).toFormat("LLL d, yyyy");
        }
        
        if (typeof dateObj === "string") {
            return DateTime.fromISO(dateObj, { zone: "utc" }).toFormat("LLL d, yyyy");
        }
        
        return dateObj;
        // return DateTime.fromJSDate(dateObj, {zone: 'utc'}).toFormat("LLL d, yyyy");
    });

    eleventyConfig.addFilter("dateFull", dateObj => {
        if (dateObj instanceof Date) {
            return DateTime.fromJSDate(dateObj).toFormat("LLLL d, yyyy");
        }
        
        if (typeof dateObj === "string") {
            return DateTime.fromISO(dateObj).toFormat("LLLL d, yyyy");
        }
        
        return dateObj;
        // return DateTime.fromJSDate(dateObj, {zone: 'utc'}).toFormat("LLLL d, yyyy");
    });

    // Get the first `n` elements of a collection.
    eleventyConfig.addFilter("head", (array, n) => {
        if(!Array.isArray(array) || array.length === 0) {
        return [];
        }
        if( n < 0 ) {
        return array.slice(n);
        }

        return array.slice(0, n);
    });

    eleventyConfig.addFilter("filterTags", function filterTagList(tags) {
		return (tags || []).filter(tag => ["featured"].indexOf(tag) === -1);
	});

    /** ======================================
    *   SHORTCODES
    *   ====================================== */

    eleventyConfig.addPairedShortcode("youtube", function(content) {
        return `<div><a href="https://www.youtube.com/watch?v=${content}" target="_blank" class="btn">Watch Related Video</a></div>`;
    });
    
    eleventyConfig.addPairedShortcode("alert", function(content) {
        return `
<div class="alert">
<div class="alert-icon">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22ZM12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20ZM11 7H13V9H11V7ZM11 11H13V17H11V11Z"></path></svg>
</div>
<div class="alert-content">
${content}
</div>
</div>
        `;
    });
    
    eleventyConfig.addPairedShortcode("details", function(content, summary) {
        content = md.render(content);
        return `
<details class="details">
<summary><span>${summary}</span><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M13.1717 12.0007L8.22192 7.05093L9.63614 5.63672L16.0001 12.0007L9.63614 18.3646L8.22192 16.9504L13.1717 12.0007Z"></path></svg></summary>
<div class="details-content article">
${content}
</div>
</details>
        `;
    });
    
    // This is a legacy shortcode. Used to display a percent bar but is now deprecated.
    eleventyConfig.addPairedShortcode("percent", function(content) {
        return `<!--<div>${content}</div>-->`;
    });

    // This is a legacy shortcode. Used to display an embedded YouTube video. Now is replaced by the "youtube" shortcode.
    eleventyConfig.addPairedShortcode("video", function(content) {
        return `<!--<div>${content}</div>-->`;
    });

    eleventyConfig.addShortcode("year", () => `${new Date().getFullYear()}`);

    /** ======================================
    *   FINALIZATIONS
    *   ====================================== */

    eleventyConfig.on('eleventy.after', () => {
        execSync(`npx pagefind`, { encoding: 'utf-8' });
    });

    return {
        dir: {
            input: '_src',
            output: '_dist'
        },
        templateFormats: ['md', 'njk', 'html'],
        dataTemplateEngine: 'njk',
        markdownTemplateEngine: 'njk'
    };
};