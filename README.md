# Dashword.net

Dashword.net is an open source Geometry Dash news outlet that publishes news, guides, reviews, opinions, lists, and all kinds of stories.

This is the third and (hopefully) final rewrite of the site. I developed this version from the ground up to minimize the need for future maintenance. But even still, I imagine there will always be a few odd jobs that could be worth doing, which is documented in `CONTRIBUTING.md`. So if you're a developer interested in helping out, give that a read!

For everyone else, you can visit our website here: [Dashword.net](https://www.dashword.net/)

## Installation

If you want to run the site locally, either to work on it or use it for your own projects:

1. Clone the repo
    ```sh
    git clone https://github.com/MoldyMacaroniX/dashword.git
    ```
2. Install NPM packages
    ```sh
    npm install
    ```
3. Run Eleventy
    ```sh
    npx eleventy --serve
    ```

This will create an instance at [http://localhost:8080/](http://localhost:8080/).

If you plan on using Dashword as a base for your own projects, that is 100% allowed, but make sure you remove any Dashword branding, our ad/analytics code in `_src/_includes/ads/`, and our articles, quizzes, courses, and podcast episodes in `_src/posts/`, `_src/courses/`, `_src/quizzes/`, and `_src/podcast/`. For more information, see `LICENSE.md`.
