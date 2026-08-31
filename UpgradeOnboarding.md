Upgrade the database and it's custom code from Odoo 16 to Odoo 19

Introduction
The goal of this task is to learn the basics of the Upgrade Process by managing the upgrade of a database with custom modules.
Feel free to roleplay with the client/reviewer (your coach) in case you need to ask him any question using the chatter.

Objective
Learning about:

Upgrade Process
Communication with customer
Subtasks and stages
PR and Git management
Investigation standard changes
Upgrading the custom code
Upgrade platform
Upgrade scripts
Testing
Studio issues
Odoo SH
Information
Custom code: https://github.com/odoo-ps/upgrade-onboarding
Database dump in the attachments or on the original task: https://www.odoo.com/odoo/project.task/5446677

Planning
Upgrade the custom code
Create a new branch on the repository to work on your task (use your n-gram in the branch name to easily identify)
Create subtasks to handle the work
Make the database installable in the new version
Test the custom features and developments
Create a PR for the upgraded code
The SH project linked to the custom code is: https://www.odoo.sh/project/upgrade-onboarding
Add yourself to the project
Create a staging branch to upgrade the database (name convention for the onboarding: 19.0-onboarding-{n-gram})
Request an upgrade for the staging branch
Test the upgraded database and share it witrh teh customer
Make sure the customisation is working in the upgraded database
Test the custom feature and developments
Test other standard flows
Fix the issues you find and reported by the customer (coach)
Once all the tickets and issues have been addressed, confirm/schedule a date for the go live with the customer
Check with your coach the steps for the go live (rehearsal and go live are not done on the onboarding, but there are specifities that are worth knowing)
Sources
Official documentation public for everyone
Upgrade process: https://www.odoo.com/documentation/master/administration/upgrade.html
How to upgrade a customized database: https://www.odoo.com/documentation/master/developer/howtos/upgrade_custom_db.html
Upgrade Scripts: https://www.odoo.com/documentation/master/developer/reference/upgrades/upgrade_scripts.html
Upgrade Utils package: https://www.odoo.com/documentation/master/developer/reference/upgrades/upgrade_utils.html
Internal Documentation
Internal process we use to upgrade our customers: https://www.odoo.com/odoo/knowledge/41896 (and sub-articles)
General knowledge (tips/tools): https://www.odoo.com/odoo/knowledge/44254 (and sub-articles)
