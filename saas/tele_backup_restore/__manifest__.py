# -*- coding: utf-8 -*-
#################################################################################
# Author      : Tele INC. (<https://tele.studio/>)
# Copyright(c): 2022-Present Tele INC.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.tele.studio/license.html/>
#################################################################################
{
  "name"                 :  "Tele Database Backup",
  "summary"              :  """Module provide feature to admin to take backups of his instance's database and later download them.""",  
  "category"             :  "Extra Tools",
  "version"              :  "1.0.4",
  "author"               :  "Tele INC.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.tele.studio/",  
  "description"          :  """Module provide feature to admin to take backups of his instance's database and later download them.""",
  "live_test_url"        :  "http://teledemo.tele.studio/demo_feedback?module=tele_backup_restore",  
  "depends"              :  [
                             'base',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/backup_process_sequence.xml',
                             'views/backup_process.xml',
                             'data/backup_ignite_crone.xml',
                             'views/menuitems.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['python-crontab']},
}
