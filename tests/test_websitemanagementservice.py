# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

import time
import unittest

from azure.servicemanagement import (
    MetricResponses,
    MetricDefinitions,
    Sites,
    Site,
    WebsiteManagementService,
    WebSpaces,
    WebSpace,
    )

from .util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    set_service_options,
    )

class WebsiteManagementServiceTest(AzureTestCase):

    def setUp(self):
        self.wss = WebsiteManagementService(credentials.getSubscriptionId(),
                                            credentials.getManagementCertFile())
        set_service_options(self.wss)

        self.created_site = None
        self.webspace_name = 'eastuswebspace'
        self.geo_region = 'East US'

    def tearDown(self):
        self.cleanup()
        return super(WebsiteManagementServiceTest, self).tearDown()

    def cleanup(self):
        if self.created_site:
            try:
                self.wss.delete_site(self.webspace_name, self.created_site)
            except:
                pass

    #--Helpers-----------------------------------------------------------------
    def _create_site(self):
        self.created_site = getUniqueName('uts')
        self.wss.create_site(
            self.webspace_name,
            self.created_site,
            self.geo_region,
            ['{0}.azurewebsites.net'.format(self.created_site)]
        )

    def _site_exists(self, webspace_name, website_name):
        try:
            site = self.wss.get_site(webspace_name, website_name)
            return True
        except:
            return False

    #--Operations for web sites ----------------------------------------
    def test_list_web_spaces(self):
        # Arrange

        # Act
        result = self.wss.list_webspaces()

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, WebSpaces)
        self.assertTrue(len(result) > 0)
        
        webspace = None
        for temp in result:
            # I need lower()?
            if temp.name.lower() == 'eastuswebspace':
                webspace = temp
                break
        self.assertEqual(webspace.geo_location, 'BLU')
        self.assertEqual(webspace.geo_region, 'East US')

    def test_get_web_space(self):
        # Arrange

        # Act
        result = self.wss.get_webspace('eastuswebspace')

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, WebSpace)
        self.assertEqual(result.geo_location, 'BLU')
        self.assertEqual(result.geo_region, 'East US')

    def test_list_web_sites(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.list_sites(self.webspace_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Sites)
        self.assertTrue(len(result) > 0)
        self.assertTrue(self._site_exists(self.webspace_name, self.created_site))

    def test_get_web_site(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.get_site(self.webspace_name, self.created_site)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Site)
        self.assertGreater(len(result.availability_state), 0)
        self.assertIn(result.compute_mode, ['Shared', 'Dedicated'])
        self.assertTrue(result.enabled)
        self.assertGreater(len(result.enabled_host_names), 0)
        self.assertGreater(len(result.host_name_ssl_states), 0)
        self.assertGreater(len(result.host_names), 0)
        self.assertEqual(result.name, self.created_site)
        self.assertEqual(result.repository_site_name, self.created_site)
        self.assertGreater(len(result.self_link), 0)
        self.assertGreater(len(result.server_farm), 0)
        self.assertIn(result.site_mode, ['Limited', 'Basic'])
        self.assertEqual(result.state, 'Running')
        self.assertEqual(result.storage_recovery_default_state, 'Running')
        self.assertEqual(result.usage_state, 'Normal')
        self.assertEqual(result.web_space, self.webspace_name)

    def test_create_site(self):
        # Arrange

        # Act
        self.created_site = getUniqueName('uts')
        result = self.wss.create_site(
            self.webspace_name,
            self.created_site,
            self.geo_region,
            ['{0}.azurewebsites.net'.format(self.created_site)]
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(self._site_exists(self.webspace_name, self.created_site))

    def test_delete_site(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.delete_site(self.webspace_name, self.created_site)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._site_exists(self.webspace_name,
                                           self.created_site))

    def test_delete_site_with_empty_farm(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.delete_site(self.webspace_name, self.created_site,
                                      delete_empty_server_farm=True)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._site_exists(self.webspace_name,
                                           self.created_site))

    def test_delete_site_with_metrics(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.delete_site(self.webspace_name, self.created_site,
                                      delete_metrics=True)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._site_exists(self.webspace_name,
                                           self.created_site))

    def test_delete_site_with_empty_farm_and_metrics(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.delete_site(self.webspace_name, self.created_site,
                                      delete_empty_server_farm=True,
                                      delete_metrics=True)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._site_exists(self.webspace_name,
                                           self.created_site))

    def test_restart_site(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.restart_site(self.webspace_name, self.created_site)

        # Assert
        self.assertIsNone(result)

    def test_get_web_site_metrics(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.get_metric_definitions(self.webspace_name,
                                                 self.created_site)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MetricDefinitions)
        self.assertGreater(len(result), 0)

        definition = result[0]
        self.assertGreater(len(definition.display_name), 0)
        self.assertGreater(len(definition.name), 0)
        self.assertGreater(len(definition.primary_aggregation_type), 0)
        self.assertGreater(len(definition.unit), 0)
        self.assertGreater(len(definition.metric_availabilities), 0)

        availability = definition.metric_availabilities[0]
        self.assertGreater(len(availability.retention), 0)
        self.assertGreater(len(availability.time_grain), 0)

    def test_get_historical_usage_metrics(self):
        # Arrange
        self._create_site()

        # Act
        result = self.wss.get_historical_usage_metrics(self.webspace_name,
                                                       self.created_site)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MetricResponses)
        self.assertGreater(len(result), 0)

        response = result[0]
        self.assertGreater(len(response.code), 0)
        self.assertIsNotNone(response.message)
        self.assertGreater(len(response.data.display_name), 0)
        self.assertGreater(len(response.data.end_time), 0)
        self.assertGreater(len(response.data.name), 0)
        self.assertGreater(len(response.data.primary_aggregation_type), 0)
        self.assertGreater(len(response.data.start_time), 0)
        self.assertGreater(len(response.data.time_grain), 0)
        self.assertGreater(len(response.data.unit), 0)
        self.assertIsNotNone(response.data.values)
