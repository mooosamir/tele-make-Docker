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
  "name"                 :  "Saas Tool",
  "summary"              :  "Saas Tool",
  "category"             :  "Extra",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Tele INC.",
  "license"              :  "Other proprietary",
  "description"          :  """Saas tools""",
  "depends"              :  [
                                'base', 'web', 'mail'
                            ],
  "data"                  : [
                              'data/ir_config_parameter.xml',
                            ],
  'assets'               : {
                             'web.assets_backend': [
                               "tele_saas_tool/static/src/css/trial_information.css",
                               "tele_saas_tool/static/src/js/trial_information.js"
                            ],
    
    },
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  True,
}
