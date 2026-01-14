# Contributing guide

Welcome to Percona ClusterSync for MongoDB (PCSM) documentation!

We're glad that you would like to become a Percona community member and help keep open source open.  

Percona ClusterSync for MongoDB is a tool for replicating data from a source MongoDB cluster to a target MongoDB cluster. It supports cloning data, replicating changes, and managing collections and indexes.

This repository contains the source file for PCSM documentation, and this document explains how you can contribute to it. 

If you'd like to submit a PCSM code patch, follow the [Contributing section in PCSM's code repository](https://github.com/percona/percona-clustersync-mongodb/blob/main/README.md#contributing). 

## Contributing to documentation

We welcome contributions from all users and the community. By contributing, you agree to the [Percona Community code of conduct](https://percona.community/contribute/coc/). Thank you for deciding to contribute and help us improve the Percona ClusterSync for MongoDB documentation.

You can contribute to the documentation in the following ways:

### Rate and comment on documentation pages

Each documentation page includes a **Rate this page** feature that allows you to assign stars (1-5) and leave comments. This is a quick and easy way to provide feedback about the documentation.

To rate a page:

1. Use the star rating system to rate the page (1-5 stars).

2. Leave a comment describing your feedback.

>[!Important]
Help us improve the documentation faster by leaving clear and detailed comments. This helps us understand the issue and address it more efficiently.

Brief comments like “this is confusing” or “needs improvement” are helpful, but sharing a bit more context allows us to take the most appropriate action.

Please include:
* What issue did you encounter, or what improvement would you like to see
* Which section or topic needs clarification or correction
* Any specific examples or use cases that would help
* The version or environment you're using (if relevant)
* Steps to reproduce any issues you found

### Add a topic in the Percona Community Forum
The [Percona Community Forum](https://forums.percona.com/) is a public discussion platform where you can ask questions, share feedback, or suggest improvements to the documentation. Use the forum to start a conversation about documentation issues, request clarifications, or discuss potential changes with the community and documentation team.

To add a topic, navigate to the [Percona Product Documentation category](https://forums.percona.com/c/percona-product-documentation/71) in the Percona Community Forum and select **New Topic**. Complete the form and select **Create Topic** to add the topic to the forum.


### Request a change with a Jira issue

Create a Jira ticket to report documentation issues or request changes. This method is useful for formal tracking or when you want the documentation team to handle the changes.

1. Open the [Percona Server Jira project](https://jira.percona.com/projects/PCSM/issues) in your browser.

2. Sign in (or create a Percona Jira account if you don't have one).

3. Click the **Create** button.

4. Fill in the required fields:

	* **Summary**: Provide a brief description of the issue.

	* **Description**: Provide more information about the issue. If needed, add a Steps To Reproduce section and information about your environment (version number, your operating system, etc.). Be detailed.

	* **Version**, **Environment**, and other relevant fields as needed.

5. Click **Create** to submit the ticket.

To go directly to the Create Issue form, use this URL: [https://jira.percona.com/secure/CreateIssue!default.jspa](https://jira.percona.com/secure/CreateIssue!default.jspa) and then select the **Percona ClusterSync for MongoDB (PCSM)** project.

### Edit the documentation yourself

Percona ClusterSync for MongoDB documentation is written in [Markdown](https://www.markdownguide.org/) language, so you can 
[edit it online via GitHub](#edit-documentation-online-via-github). If you wish to have more control over the doc process, jump to how to [edit documentation locally](#edit-documentation-locally). 

Before you start, learn what git, MkDocs, and Markdown are, and how to write them. For your convenience, a cheat sheet is also available to assist you with the syntax. 

The doc files are in the `docs` directory.

#### Edit documentation online via GitHub

1. Click the **Edit this page** banner. The source `.md` file of the page opens in GitHub editor in your browser. If you haven’t worked with the repository before, GitHub creates a [fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) of it for you.

2. Edit the page. You can check your changes on the **Preview** tab.

3. Commit your changes.

	 - In the **Commit changes** section, describe your changes.
	 - Select the **Create a new branch for this commit and start a pull request** option
	 - Click **Propose changes**.

4. GitHub creates a branch and a commit for your changes. It loads a new page on which you can open a pull request to Percona. The page shows the base branch - the one you offer your changes for, your commit message, and a diff - a visual representation of your changes against the original page.  This allows you to make a last-minute review. When you are ready, click the **Create pull request** button.
5. Someone from our team reviews the pull request and, if everything is correct, merges it into the documentation. Then it gets published on the site.

#### Edit documentation locally

This option is for users who prefer to work from their computer and/or have full control over the documentation process.

The steps are the following:

1. Fork this repository
2. Clone the repository on your machine:

```sh
git clone git@github.com:<your_name>/pcsm-docs.git
```

3. Change the directory to ``pcsm-docs`` and add the remote upstream repository:

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

6. Make changes.
7. Check your changes. Some editors (Sublime Text, VSCode, and others) have the Markdown preview, which you can use to check how the page is rendered. Alternatively, you can [build the documentation](#building-the-documentation) to know exactly how the documentation looks on the website.
8. Commit your changes. The [commit message guidelines](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53) will help you with writing great commit messages

9. Open a pull request to Percona

### Building the documentation

To verify how your changes look, generate the static site with the documentation. This process is called *building*. You can do it as follows:

#### Install MkDocs and build locally

1. Install [Python](https://www.python.org/downloads/).

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

## After your pull request is merged

Once your pull request is merged, you are an official Percona Community Contributor. Welcome to the community!

