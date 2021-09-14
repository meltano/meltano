---
title: "Marketing Ops"
sidebarDepth: 2
---


# Marketing Ops

Please see a full list of all our [tooling here](https://meltano.com/handbook/tech-stack/).

## Website/blog

The website and blog are currently hosted on SiteGround. You can find the credentials in 1Password.

### WordPress

WordPress has automatic updates enabled so that we always run the latest stable release.

#### Plugins

Plugins are also automatically updated and typically update overnight. A ticket is automatically created in ZenDesk whenever plugins are updated.

##### Jetpack

You can configure the social media buttons that appear on posts [here](https://meltano.com/blog/wp-admin/options-general.php?page=sharing).

##### Permalink Manager

You can update the permalinks for a post through the post's settings or through this [list](https://meltano.com/blog/wp-admin/tools.php?page=permalink-manager).

### Troubleshooting

#### Website redirects to defaultwebpage.cgi

It's not clear why this happens, but clearing the cache resolves it. Follow SiteGround's instructions to [clear the cache](https://www.siteground.com/kb/clear-site-cache/). See [this issue](https://gitlab.com/meltano/meltano/-/issues/2886) for more information.

## Intercom

## Social

## Design

## Newsletter

## Community Management Tools

## Slack

### Slack Invite URL

[https://meltano.com/slack](https://meltano.com/slack) points to an invite to join our Slack workspace. The Slack links we generate can be used 2,000 times and do not expire.

1. **Generate an invite URL in Slack.** 
  1. On Slack, click "Meltano" in the top left menu and select "Invite people to Meltano".
  1. Click "Edit link settings" and create a new link with no expiry.
    1. **Note:** You can also deactivate the invite URL entirely from here if needed. Please proceed with caution as `https://meltano.com/slack` is linked in our documentation and marketing materials.
  1. Copy and save the link for the next step.
1. Edit SiteGround
  1. Log into SiteGround using the credentials in 1Password
  1. Visit the [Redirects](https://tools.siteground.com/redirect) page and click the pencil icon next to `https://meltano.com/slack`.
  1. Keep the "Redirect Type" set to "Permanent (301)" and replace the existing Slack invite with the new one from above.
  1. Click "Confirm". It may take several minutes for [https://meltano.com/slack](https://meltano.com/slack) to point to the new invite.
