# Notion Automations

This repository is focused on all my notion integrations that focused to help on daily tasks and is a work in progress.

Those automations are suposed to run on a AWS Lambda server, utilizing the power of notion webhooks to trigger the automations.

# Automations

The automations are separated by foders, which will be trigged by a webhook sent by Notion.

## Integrantes

This automation is meant to run once in a day and when called, get a list of participants and its bith dates, described in a given Notion Database. By comparing to the actual day, an email to the users in database will be sent when the it is detected that is their birthday.   
