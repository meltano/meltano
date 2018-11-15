import pytest
import json
from unittest import mock
from pathlib import Path

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer import CatalogSelectAllVisitor


CATALOG = """
{
  "streams": [
    {
      "tap_stream_id": "Account",
      "stream": "Account",
      "key_properties": [
        "Id"
      ],
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "AccountCode__c": {
            "type": [
              "string",
              "null"
            ]
          },
          "AccountNumber": {
            "type": [
              "string",
              "null"
            ]
          },
          "AdditionalEmailAddresses": {
            "type": [
              "string",
              "null"
            ]
          },
          "AllowInvoiceEdit": {
            "type": [
              "boolean",
              "null"
            ]
          },
          "AutoPay": {
            "type": [
              "boolean",
              "null"
            ]
          },
          "Balance": {
            "type": [
              "number",
              "null"
            ]
          },
          "Batch": {
            "type": [
              "string",
              "null"
            ]
          },
          "BcdSettingOption": {
            "type": [
              "string",
              "null"
            ]
          },
          "BillCycleDay": {
            "type": [
              "integer",
              "null"
            ]
          },
          "CommunicationProfileId": {
            "type": [
              "string",
              "null"
            ]
          },
          "ConversionRate__c": {
            "type": [
              "string",
              "null"
            ]
          },
          "CreatedById": {
            "type": [
              "string",
              "null"
            ]
          },
          "CreatedDate": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "CreditBalance": {
            "type": [
              "number",
              "null"
            ]
          },
          "CrmId": {
            "type": [
              "string",
              "null"
            ]
          },
          "Currency": {
            "type": [
              "string",
              "null"
            ]
          },
          "CustomerServiceRepName": {
            "type": [
              "string",
              "null"
            ]
          },
          "Entity__c": {
            "type": [
              "string",
              "null"
            ]
          },
          "Id": {
            "type": [
              "string",
              "null"
            ]
          },
          "InvoiceDeliveryPrefsEmail": {
            "type": [
              "boolean",
              "null"
            ]
          },
          "InvoiceDeliveryPrefsPrint": {
            "type": [
              "boolean",
              "null"
            ]
          },
          "InvoiceTemplateId": {
            "type": [
              "string",
              "null"
            ]
          },
          "LastInvoiceDate": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "Mrr": {
            "type": [
              "number",
              "null"
            ]
          },
          "Name": {
            "type": [
              "string",
              "null"
            ]
          },
          "Notes": {
            "type": [
              "string",
              "null"
            ]
          },
          "Parent__c": {
            "type": [
              "string",
              "null"
            ]
          },
          "ParentId": {
            "type": [
              "string",
              "null"
            ]
          },
          "PaymentGateway": {
            "type": [
              "string",
              "null"
            ]
          },
          "PaymentTerm": {
            "type": [
              "string",
              "null"
            ]
          },
          "PurchaseOrderNumber": {
            "type": [
              "string",
              "null"
            ]
          },
          "SalesRepName": {
            "type": [
              "string",
              "null"
            ]
          },
          "SFDC_Sync__c": {
            "type": [
              "string",
              "null"
            ]
          },
          "Status": {
            "type": [
              "string",
              "null"
            ]
          },
          "Support_Hold__c__c": {
            "type": [
              "string",
              "null"
            ]
          },
          "TaxCompanyCode": {
            "type": [
              "string",
              "null"
            ]
          },
          "TaxExemptCertificateID": {
            "type": [
              "string",
              "null"
            ]
          },
          "TaxExemptCertificateType": {
            "type": [
              "string",
              "null"
            ]
          },
          "TaxExemptDescription": {
            "type": [
              "string",
              "null"
            ]
          },
          "TaxExemptEffectiveDate": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "TaxExemptEntityUseCode": {
            "type": [
              "string",
              "null"
            ]
          },
          "TaxExemptExpirationDate": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "TaxExemptIssuingJurisdiction": {
            "type": [
              "string",
              "null"
            ]
          },
          "TaxExemptStatus": {
            "type": [
              "string",
              "null"
            ]
          },
          "TotalDebitMemoBalance": {
            "type": [
              "number",
              "null"
            ]
          },
          "TotalInvoiceBalance": {
            "type": [
              "number",
              "null"
            ]
          },
          "UnappliedBalance": {
            "type": [
              "number",
              "null"
            ]
          },
          "UnappliedCreditMemoAmount": {
            "type": [
              "number",
              "null"
            ]
          },
          "UpdatedById": {
            "type": [
              "string",
              "null"
            ]
          },
          "UpdatedDate": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "VATId": {
            "type": [
              "string",
              "null"
            ]
          },
          "BillToContactId": {
            "type": [
              "string",
              "null"
            ]
          },
          "DefaultPaymentMethodId": {
            "type": [
              "string",
              "null"
            ]
          },
          "ParentAccountId": {
            "type": [
              "string",
              "null"
            ]
          },
          "SoldToContactId": {
            "type": [
              "string",
              "null"
            ]
          },
          "Deleted": {
            "type": "boolean"
          }
        }
      },
      "metadata": [
        {
          "breadcrumb": [
            "properties",
            "AccountCode__c"
          ],
          "metadata": {
              "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "AccountNumber"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "AdditionalEmailAddresses"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "AllowInvoiceEdit"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "AutoPay"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Balance"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Batch"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "BcdSettingOption"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "BillCycleDay"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CommunicationProfileId"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "ConversionRate__c"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CreatedById"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CreatedDate"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CreditBalance"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CrmId"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Currency"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CustomerServiceRepName"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Entity__c"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Id"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "InvoiceDeliveryPrefsEmail"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "InvoiceDeliveryPrefsPrint"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "InvoiceTemplateId"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "LastInvoiceDate"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Mrr"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Name"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Notes"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Parent__c"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "ParentId"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "PaymentGateway"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "PaymentTerm"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "PurchaseOrderNumber"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "SalesRepName"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "SFDC_Sync__c"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Status"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Support_Hold__c__c"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxCompanyCode"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptCertificateID"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptCertificateType"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptDescription"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptEffectiveDate"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptEntityUseCode"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptExpirationDate"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptIssuingJurisdiction"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TaxExemptStatus"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TotalDebitMemoBalance"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "TotalInvoiceBalance"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "UnappliedBalance"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "UnappliedCreditMemoAmount"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "UpdatedById"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "UpdatedDate"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "VATId"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "BillToContactId"
          ],
          "metadata": {
            "tap-zuora.joined_object": "BillToContact",
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "DefaultPaymentMethodId"
          ],
          "metadata": {
            "tap-zuora.joined_object": "DefaultPaymentMethod",
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "ParentAccountId"
          ],
          "metadata": {
            "tap-zuora.joined_object": "ParentAccount",
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "SoldToContactId"
          ],
          "metadata": {
            "tap-zuora.joined_object": "SoldToContact",
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Deleted"
          ],
          "metadata": {
            "inclusion": "available"
          }
        }
      ],
      "replication_key": "UpdatedDate",
      "replication_method": "INCREMENTAL"
    },
    {
      "tap_stream_id": "AccountingCode",
      "stream": "AccountingCode",
      "key_properties": [
        "Id"
      ],
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "Category": {
            "type": [
              "string",
              "null"
            ]
          },
          "CreatedById": {
            "type": [
              "string",
              "null"
            ]
          },
          "CreatedDate": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "GLAccountName": {
            "type": [
              "string",
              "null"
            ]
          },
          "GLAccountNumber": {
            "type": [
              "string",
              "null"
            ]
          },
          "Id": {
            "type": [
              "string",
              "null"
            ]
          },
          "Name": {
            "type": [
              "string",
              "null"
            ]
          },
          "Notes": {
            "type": [
              "string",
              "null"
            ]
          },
          "Status": {
            "type": [
              "string",
              "null"
            ]
          },
          "Type": {
            "type": [
              "string",
              "null"
            ]
          },
          "UpdatedById": {
            "type": [
              "string",
              "null"
            ]
          },
          "UpdatedDate": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "Deleted": {
            "type": "boolean"
          }
        }
      },
      "metadata": [
        {
          "breadcrumb": [
            "properties",
            "Category"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CreatedById"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "CreatedDate"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "GLAccountName"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "GLAccountNumber"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Id"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Name"
          ],
          "metadata": {
            "inclusion": "automatic"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Notes"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Status"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Type"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "UpdatedById"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "UpdatedDate"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "Deleted"
          ],
          "metadata": {
            "inclusion": "available"
          }
        }
      ],
      "replication_key": "UpdatedDate",
      "replication_method": "INCREMENTAL"
    }
  ]
}
"""


class TestSingerTap:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.EXTRACTORS, "tap-first")

    def config_files(self, subject, dir: Path):
        return {key: dir.join(file) for key, file in subject.config_files.items()}

    def test_exec_args(self, subject, tmpdir):
        base_files = self.config_files(subject, tmpdir.mkdir("base"))
        assert subject.exec_args(base_files) == ["--config", base_files["config"]]

        # when `catalog` has data
        base_files = self.config_files(subject, tmpdir.mkdir("catalog"))
        base_files["catalog"].open("w").write("...")
        assert subject.exec_args(base_files) == [
            "--config",
            base_files["config"],
            "--catalog",
            base_files["catalog"],
        ]

        # when `state` has data
        base_files = self.config_files(subject, tmpdir.mkdir("state"))
        base_files["state"].open("w").write("...")
        assert subject.exec_args(base_files) == [
            "--config",
            base_files["config"],
            "--state",
            base_files["state"],
        ]

    def test_run_discovery(self, project, subject):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 0

        invoker = PluginInvoker(project, subject)
        invoker.prepare()

        with mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke:
            subject.run_discovery(invoker, [])

            assert invoke.called_with(["--discover"])

    def test_run_discovery_fails(self, project, subject):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 1  # something wrong happened

        invoker = PluginInvoker(project, subject)
        invoker.prepare()

        with mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke:
            subject.run_discovery(invoker, [])

            assert not invoker.files[
                "catalog"
            ].exists(), "Catalog should not be present."

    def test_run_discovery_invalid(self, project, subject):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 0

        invoker = PluginInvoker(project, subject)
        invoker.prepare()

        def corrupt_catalog(*_, **__):
            invoker.files["catalog"].open("w").write("this is invalid json")

            return process_mock

        with mock.patch.object(
            PluginInvoker, "invoke", side_effect=corrupt_catalog
        ) as invoke:
            subject.run_discovery(invoker, [])

            assert not invoker.files[
                "catalog"
            ].exists(), "Catalog should not be present."


class TestCatalogSelectVisitor:
    @pytest.fixture
    def catalog(self):
        return json.loads(CATALOG)

    @classmethod
    def stream_is_selected(cls, stream):
        return stream.get("selected", False)

    @classmethod
    def metadata_is_selected(cls, metadata):
        inclusion = metadata.get("inclusion")
        if inclusion == "automatic":
            return true

        if inclusion == "available":
            return metadata.get("selected", False)

    def test_visitor(self, catalog):
        CatalogSelectAllVisitor.visit(catalog)

        streams = (stream for stream in catalog["streams"])
        metadata = (metadata for stream in streams for metadata in stream["metadata"])

        # everything is selected
        assert all(map(self.stream_is_selected, streams))
        assert all(map(self.metadata_is_selected, metadata))


class TestSingerTarget:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.LOADERS, "target-csv")

    def test_exec_args(self, subject):
        base_files = subject.config_files
        assert subject.exec_args(base_files) == ["--config", base_files["config"]]
