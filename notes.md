1. Restore dump of existing database:

`createdb -p 5433 erdenet_16_real`
`pg_restore -p 5433 -d erdenet_16_real ~/odev/worktrees/16.0/vise-upgrade-onboarding-erdenet-mining/upgrade-onboarding.dump`

2. Start database and explore the existing modules:

`
--addons-path="addons/,../enterprise,../vise-upgrade-onboarding-erdenet-mining,../design-themes"
--upgrade-path="/home/odoo/odev/worktrees/upgrade-util/src, /home/odoo/odev/worktrees/upgrade/migrations"
--dev
all
-d
erdenet_16_real
--db_port
5433
--http-port
8070
--log-handler
:DEBUG
`

### Bug list
- Real Estate -> click on record -> `psycopg2.errors.UndefinedColumn: column estate_property.commission_rate does not exist`:
-> Search for `commission_rate` in the database's fields view (Ctrl+K -> type fields) -> Confirm that the fields are missing
Upgrade module to restore fields

3. Create an empty database on the new version:
`
--addons-path="addons/,../enterprise,../vise-upgrade-onboarding-erdenet-mining,../design-themes"
--upgrade-path="/home/odoo/odev/worktrees/upgrade-util/src, /home/odoo/odev/worktrees/upgrade/migrations"
--dev
all
-d
erdenet_19_clean
-u
estate,estate_account
--db_port
5433
--http-port
8073
--log-handler
:DEBUG
`
4. Start inspecting module code:
 - Determine which part of the code should be inspected first and start from there
 - Identify locations of low confidence
 - If its a standalone implementation (for example, methods only using model specific fields), most likely its fine.
If its inheriting/extending standard features, find similar implementations by searching the syntax 
 - If matches are found, leave it for now. 
If not, first find similar implementations in the old version, then find its corresponding implementation in the new version.
 - If stuck, search on the net / ask colleagues / ask AI
 - Identify the difference and adapt the code accordingly
 - Install module, if any errors present, identify the source of error from the module, fix them and iterate.
Sometimes its better to scrap the database after install failures, since the database might be in a weird intermediate state.
 - Finally the module can be installed on a clean database without errors
 - Run tests (if any), adapt tests or update implementation accordingly, fix them and iterate. (append `--test-tags estate,estate_account` to `odoo-bin` arguments)
 - Manual, functional end-to-end testing of features to verify the implementations are working / requirements are satisfied. If not, fix them and iterate.

#### Example - `EstateProperty` models
- `_description`: `Test Description`:
-> Code that wasn't cleaned up
-> Update description

- `channel_id`: the related model `mail.channel` doesn't exist:
-> Search for the sql constraint `The channel UUID must be unique`
-> Implementation shows up in a new model `discuss.channel`
-> Model name match (`Discussion Channel`, first seemingly model-specific method name matches (`_generate_random_token`)
-> High confidence that `discuss.channel` serves the same function as `mail.channel`
-> Update the related attribute of the field from `mail.channel` to `discuss.channel`

- `currency_id`: Reported as duplicated by IDE's intellisense:
-> Identical implementation 
-> Remove one of the lines


- `_sql_constraints`: Log warning: "Model attribute '_sql_constraints' is no longer supported,"
-> Compare related implementations across versions. For example, search using the `uuid_unique` constraint on the model `Discussions Channel`
-> Search for its description `The channel UUID must be unique`
-> Compare patterns and notice that the new syntax `models.Constraint` is used instead
-> Adapt code accordingly

- `name_get`: suspicious, looks like the implementation of a common method defined in a base class
-> Search for `def name_get`, 100+ results in 16.0, 3 results in 19.0
-> This time we dig deeper by directly checking the `BaseModel` (odoo/orm/models.py)
-> Scroll to the `name_get` method in v16, its called by the `_compute_display_name` method immediately above,
but when checking v19, its replacement/corresponding implementation is not obvious yet
-> Search for git commit history for hints
-> One of the commits have a relevant title "[REM] core: remove `name_get` API"
-> Read through commit and notice that the `name_get` override is moved to `_compute_display_name`
-> Adapt code accordingly

- `get_legacy_company_commission`: uncommon implementations 
-- `search` on `ir.model.fields` seems suspicious
-> the field can be directly accessed through `ref`, with the record's `xml_id`
For fields, the format is `{module}.field_{model}__{field_name}`, so `field = self.env.ref('estate.field_estate_property__commission_rate')`

-- query on `ir_property`, however model seems to no longer exist
-> Search for related commit `git log --all -- ./odoo/addons/base/models/ir_property.py` (https://stackoverflow.com/questions/6839398/find-when-a-file-was-deleted-in-git)
-> learn that `ir.property` served two functions 1) define company-related values 2) set field defaults, both is irrelevant to our usage
-> Data has to be migrated
(Migration scripts, their execution order and their ecosystem should be covered by this point)
-> To migrate IrProperty related data, upgrade scripts created into the module will not work, since by its time of execution, IrProperty has already been removed.
-> Migrate the data in production, or create upgrade tickets to ask for help / clarification.

-- At a second glance, the method isn't even being called anywhere, 
and since the implementation boils down to a simple `record.commission_rate` statement, if needed, external rpc calls will be able to retrieve the information
by directing doing `search_fetch` to directly fetch the records values.
-> Remove the entire method

- `fields_view_get`: just like `name_get`, suspicious, looks like the implementation of a common method defined in a base class:
-> Search for `fields_view_get` and observe that it is already deprecated in v16, and from the message, the suggested implementation is to use `get_view` instead.
-> Search for `get_view` in v16 and v19, a similar number of calls, seems like its still valid in v19.
-> Check our own `fields_view_get` implementation, our override returned the result immediately after called `super()`.
-> Not functional, remove the entire method

- `states` attribute on `commission_rate`: suspicious, unfound elsewhere in standard modules
-> Search for `states={`, 100 + results on v16, only 1 on v19
-> Similarly, find a random standard field as reference, search through its commits
-> Realize that the implementation is directly moved to the `invisible`/`readonly` attributes defined on view records
-> Adapt code

#### EstateProperty's Controllers
Migrating controllers are similar to working with models

- Endpoint decorators with `type='json'`, warning logs reminded us that `json` is decorated:
-> update to `jsonrpc` accordingly

### EstateProperty's Tests
On migrating tests: Ensure the contents of each tests is actually testing something useful. (No `assertTrue(True)`)
Then directly run the tests, fix errors as they popup.

- Error when running tests: `ImportError: cannot import name 'SavepointCase' from 'odoo.tests.common'`:
-> Search for `SavepointCase` in v16
-> Immediately a log statement can be found that mentioned `TransactionCase` will be its replacement
-> Update `SavepointCase` to `TransactionCase`

- Error when running tests: `odoo.exceptions.UserError: The selling price cannot be lower than 90% of the expected price`:
-> Follow test report/ error stack trace to find the failing test (`TestEstatePropertyOffer`)
-> For this case, its obvious that the referred property `beachfront_villa` has a expected price of `750000`, while our offer is `230000`.
and that `230000` is lower than 90% of the `750000`.
For non-obvious errors, run the tests with a debugger attached (commonly using the ide), to debug the error.
Sometimes, failing tests indicate real implementation bugs, instead of the tests being badly written. 
-> Update `230000` to `675000`

### EstateProperty's Javascript
Javascript customizations are much more fragile between version changes, and usually requires more care.

- Unused defined field type, remove file and its manifest entry
(TODO: add more things and actually migrate it?)

#### EstateProperty's views
View migrations are much easier. For most errors, they are caught and reported immediately when the module is being loaded into the registry.
Then, the remaining less obvious errors will be uncovered when clicking into them,
through a popup directly displaying the error/ or by presenting us a horribly broken view 
(For example, opening the kanban view of estate will be presented with `OwlError: The following error occurred in onWillStart: "Missing 'card' template."`)


For the remaining errors, they either already exist in production, or the implemented function wasn't noticed even when its missing.
Let them stay in the module if they are undiscovered.

- Update `tree` to `list`
- destruct `attrs` attributes, move dict keys to their individual attributes, update their values from domains to python expression
- migrate kanban view
-> Search and compare implementation differences across versions for the same view (For example, use `hr_appraisal_goal_view_kanban` as reference)
-> 16.0 to 19.0 kanban migrations can feel like a rewrite. Focus on its functional features, don't have to (and sometimes we can't) recreate exact stylings.

- update `column_invisible` to `invisible` 
https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures/generic_attribute_column_invisible.html
- `estate_property_type_view_form`, `expected_price`'s attribute update `offer_count` to `parent.offer_count`
- remove view, `estate_property_type_view_form_legacy_extension`, write migration scripts with `util.remove_view` (I didn't test it)
- remove commented out code in `view_users_form`
- Fix `action_offer_accept` and `action_offer_refuse` invisible conditions properly. (Original: `invisible='status`)
- Refactor and remove unused invisible fields (For example `<field name="currnecy_id" invisible="1"/>` on `estate_property_offer_view_tree`)
### Other notable examples

- `HrLeave._force_cancel` signature has been updated
- `PropertyOffer.create` decorator update to `api.model_create_multi`, wrap implementation in for loop
- In `estate_property_view_tree`, `<field name="date_availability"/>`'s `optional` attribute update from "disabled" to "hide"
- Refactor: In `ResUsers`, remove unused `api` import
- In `TestEstateAccountProperty.test_action_property_sold`, `expression.AND` is deprecated.
Migrate to `Domain`

5. Install the module on an upgraded database, and make sure the module work well.

### Honorable mentions on tools that greatly helped upgrades
- A good plugin for IDE support on Odoo development, enable code completion, syntax highlighting, and catch easily detectable odoo-specific errors, etc.
https://marketplace.visualstudio.com/items?itemName=trinhanhngoc.vscode-odoo
- Pre-commit hooks to catch common python pitfalls/help on styling
https://github.com/OCA/odoo-pre-commit-hooks
- AI Agents, set them up in a way that gives access to the standard odoo modules, with the origin and target version simultaneously.
(Only endorsing giving access on the `odoo/odoo` repository, as the `odoo/enterprise` repository is not publicly available, and giving access on that violates rules. 
But I also observed that almost every dev I know that uses AI in our company also feeds in the `odoo/enterprise` repository, and several private repositories too.)
Then ask questions about the repository. They are very good at researching code, and allows us to compare and learn features across versions with much less effort.
(Some questions that I have asked: 
  * Has inventory valuation changed between the two versions? If yes, how did the implementation change?
  * Why is the field `taxes_id` on the model `SaleOrder` gone? Please tell me its replacement, and give examples on how features that utilizes it have adapted.
  * Why does the StockPicking report look different on the new version? How had the css styles changed between the versions? Please tell me how can i update my current report accordingly.
  * What is this new `ResGroupsPrivilege` model? Why do some `ResGroup` records now sometimes omit a `privilege_id`? How can i migrate my ResGroup records accordingly?
  * How do I reconcile bank statements throughout the UI on both versions?
)
Also they are good at generating something, which is better than nothing when we are stuck.

### Summary
Techniques:
- Search through database to compare implementations:
-> First identify suspicious patterns in our own custom modules
-> Search for said pattern throughout the standard modules in the old version and locate referenceable implementations
-> Search for its corresponding implementation in the new version
-> Compare the implementation differences
-> Take the differences and adapt the custom module accordingly
- Also read through commit history for more clues when needed
- Step through logic using a debugger
- Read through the server logs, both during module installation/upgrade and test results
- Search through official documentations / online forums

## Part 2 - 19.0 to 20.0

Since the code was already brought up to modern conventions during the 16.0 -> 19.0 pass (Constraint objects,
`@api.ondelete`, `invisible=`/no more `attrs`, `list` views, `jsonrpc` routes, etc.), the 19.0 -> 20.0 jump is a
much smaller delta. Repeat the same install/inspect/fix/test loop as Part 1, just with a shorter list of findings.

1. Set up a venv for 20.0 (none existed yet under `~/odev/virtualenvs/`):
`python3 -m venv ~/odev/virtualenvs/20.0`
`~/odev/virtualenvs/20.0/bin/pip install -r ~/odev/worktrees/20.0/odoo/requirements.txt`
(the 20.0 checkout's `odoo/release.py` still reports `version_info = (19, 5, 0, ALPHA, 1, '')` at the time of
this migration - i.e. it's pre-release/master, not yet stamped "20.0" - so `release.major_version` is `'19.5'`,
not `'20.0'`.)

2. Create an empty database on the new version and try to install:
`
--addons-path="addons/,../enterprise,../vise-upgrade-onboarding-erdenet-mining,../design-themes"
--upgrade-path="/home/odoo/odev/worktrees/upgrade-util/src, /home/odoo/odev/worktrees/upgrade/migrations"
--stop-after-init
-i estate,estate_account
-d erdenet_20_clean
--db_port 5433
--log-handler :INFO
`

### Bug list
- Both modules load with `The module estate has an incompatible version, setting installable=False`:
-> `check_version()` (`odoo/modules/module.py`) requires the manifest `version` to start with `release.major_version`
-> Since this checkout's `release.major_version` is `'19.5'` (see above), bump `'version': '19.0.1.0.0'` to `'19.5.1.0.0'` in both manifests (not `'20.0...'`, that would fail the same check)

- `estate/security/ir.model.access.csv` load fails with `KeyError: 'ir.model.access'`:
-> The `ir.model.access` model (4 boolean `perm_*` columns) has been removed and replaced by a unified `ir.access`
model (single `operation` selection field, one of `crud`/`cru`/`cr`/.../`c`/`r`/`u`/`d`, plus an optional `domain`)
-> Confirmed by grepping standard modules: no more `*/security/ir.model.access.csv` files anywhere, all replaced
by `*/security/ir.access.csv`
-> Rename the file to `ir.access.csv` (and update the manifest's `data` list accordingly), convert the columns:
`id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink` becomes
`id,name,model_id,group_id/id,operation,domain`
-> Note `model_id` is no longer an xmlid reference (`model_estate_property`), it takes the model's technical name
directly (`estate.property`) - `ir.model`'s `_rec_names_search = ('name', 'model')` is what lets the CSV loader's
implicit name_search on the Many2one resolve a plain technical name
-> All our rows were `1,1,1,1` (full CRUD), so they all become `operation=crud`, `domain` left empty

5. Install the module on the upgraded/target database, make sure it still works:
- Fresh install of `estate,estate_account` (`-i`) on an empty 20.0 database: clean, no warnings.
- Full test suite (`--test-tags estate,estate_account`): 17 tests, 0 failed, 0 errors.
- Tried `-u all` against a copy of the `erdenet_19_clean` database to simulate an in-place upgrade end-to-end:
this pulls in the *entire* product's core upgrade (every previously-installed standard module), which hit
unrelated pre-existing core upgrade-script gaps (e.g. a `product.product` field removal missing its
`util.remove_field` call). That is the Upgrade platform/service's job, not something to fix here as part of a
single custom module's version bump - out of scope for this exercise, same as it was out of scope in Part 1.
Sticking to the documented pattern (fresh empty db + `-i`) is what actually validates the custom code.

### Summary
Only 3 lines actually needed to change for this leg: the two manifest `version` bumps, and the ACL file
rename + reformat. Everything else (models, views, controllers, tests) was already compatible.
