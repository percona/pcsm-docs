# Contributing guide

Welcome to Percona ClusterSync for MongoDB documentation!

We're glad that you would like to become a Percona community member and participate in keeping open source open.  

Percona ClusterSync for MongoDB is a tool for replicating data from a source MongoDB cluster to a target MongoDB cluster. It supports cloning data, replicating changes, and managing collections and indexes.

This repository contains the source file for PCSM documentation and this document explains how you can contribute to it. 

If you'd like to submit a PCSM code patch, follow the [Contributing section in PCSM's code repository](https://github.com/percona/percona-clustersync-mongodb/blob/main/README.md#contributing). 

## Contributing to documentation

Percona ClusterSync for MongoDB documentation is written in [Markdown] language, so you can 
[edit it online via GitHub](#edit-documentation-online-via-github). If you wish to have more control over the doc process, jump to how to [edit documentation locally](#edit-documentation-locally). 

Before you start, learn what [git], [MkDocs] and [Docker] are and what [Markdown] is and how to write it. For your convenience, there's also a cheat sheet to help you with the syntax. 

The doc files are in the `docs` directory.

### Edit documentation online via GitHub

1. Click the <img src="_resource/.icons/edit_page.png" width="20px" height="20px"/> **Edit this page**. The source `.md` file of the page opens in GitHub editor in your browser. If you haven't worked with the repository before, GitHub creates a [fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) of it for you.

2. Edit the page. You can check your changes on the **Preview** tab.

3. Commit your changes.

	 - In the *Commit changes* section, describe your changes.
	 - Select the **Create a new branch for this commit and start a pull request** option
	 - Click **Propose changes**.

4. GitHub creates a branch and a commit for your changes. It loads a new page on which you can open a pull request to Percona. The page shows the base branch - the one you offer your changes for, your commit message and a diff - a visual representation of your changes against the original page.  This allows you to make a last-minute review. When you are ready, click the **Create pull request** button.
5. Someone from our team reviews the pull request and if everything is correct, merges it into the documentation. Then it gets published on the site.

### Edit documentation locally

This option is for users who prefer to work from their computer and / or have the full control over the documentation process.

The steps are the following:

1. Fork this repository
2. Clone the repository on your machine:

```sh
git clone git@github.com:<your_name>/pcsm-docs.git
```

1. Change the directory to `pcsm-docs` and add the remote upstream repository:

```sh
git remote add upstream git@github.com:percona/pcsm-docs.git
```

4. Pull the latest changes from upstream

```sh
git fetch upstream
git merge upstream/main
```

5. Create a separate branch for your changes

```sh
git checkout -b <my_branch>
```

6. Make changes. See the [Repository structure](#repository-structure) to for details what files this repo contains and their purpose.
7. Check your changes. Some editors (Sublime Text, VSCode and others) have the Markdown preview which you can use to check how the page is rendered. Alternatively, you can [build the documentation](#building-the-documentation) to know exactly how the documentation looks on the web site.
8. Commit your changes. The [commit message guidelines](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53) will help you with writing great commit messages

9. Open a pull request to Percona

### Building the documentation

To verify how your changes look, generate the static site with the documentation. This process is called *building*. 

#### Preconditions

1. Install [Python].

2. Install MkDocs and required extensions:

    ```sh
    pip install -r requirements.txt
    ```

#### Build the site

1. To build the site, run:

    ```sh
    mkdocs build
    ```

2. Open `site/index.html`

#### Live preview

To view your changes as you make them, run the following command:

```sh
mkdocs serve
```

Paste the <http://127.0.0.1:8000> in your browser and you will see the documentation. The page reloads automatically as you make changes.

#### PDF

To build the PDF documentation, open the `site/print_page.html` in your browser. Save it as PDF. Depending on the browser, you may need to select the Export to PDF, Print - Save as PDF or just Save and select PDF as the output format.


## After your pull request is merged

Once your pull request is merged, you are an official Percona Community Contributor. Welcome to the community!

## Repository structure

The repository includes the following directories and files:

- `mkdocs-base.yml` - the base configuration file. It includes general settings and documentation structure.
- `mkdocs.yml` - configuration file. Contains the settings for building the docs with Material theme.
- `mkdocs-pdf.yml` - configuration file. Contains the settings for building the PDF docs.
- `docs`:
  - `*.md` - Source markdown files.
  - `_images` - Images, logos and favicons
  - `css` - Styles
  - `js` - Javascript files
- `_resource`:
   - `templates`:
     - ``styles.scss`` - Styling for PDF documents
   - `theme`:
      - `main.html` - The layout template for hosting the documentation on Percona website
   - overrides - The folder with the Material theme template customization for builds
- `site` - This is where the output HTML files are put after the build


[MkDocs]: https://www.mkdocs.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[Git]: https://git-scm.com
[Python]: https://www.python.org/downloads/
[Docker]: https://docs.docker.com/get-docker/
