# Using FTP with Meltano

Some extractors require you to place a file with credentials or other information inside your Meltano project. This is easy when your project lives on your local machine, but not quite as straightforward for project hosted on meltanodata.com.

When you need to upload files into your Meltano project on meltanodata.com, we recommend using FTP (File Transfer Protocol). This will allow you to login to your Meltano project and interact with it similar to how you would work with any directory on your computer.

## Getting Started

There are many options when it comes to FTP software. A great option we recommend is [FileZilla](https://filezilla-project.org/) since it works on all platforms and is 100% free! As a result, we will be using it for the remainder of this tutorial.

<iframe width="560" height="315" src="https://www.youtube.com/embed/q9I4ZxQvfdg" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="mt-2r"></iframe>

## How to Connect to Your Meltano Project

First, we will start by saving a new connection in FileZilla.

1. Click on `File` > `Site Manager`
2. Once the "Site Manager" window pops up, click the `New Site` button
3. Name your site with your desired name and Meltano to make it easy to distinguish (Example: `GitLab - Meltano`)
4. Fill out the form on the right with the following information:

- **Host**: \$YOUR_PROJECT_NAME.meltanodata.com
- **Port**: 2021
- **User**: meltano_ftp
- **Password**: Given to you by your account manager

5. Now you can click `Connect` and you should see your files on the right side of FileZilla!

To upload files, all you need to do is:

1. Locate the files on the left panel (which contains your local files on your computer)
2. Open the directory you want the file to live in on the server
   - Most extractors look for their files in the project root directory: the first directory you'll see after connecting
3. Click and drag the file from the left panel into the right panel

Once you see the file appear on the right panel, your upload is successfully uploaded onto the server! :tada:
