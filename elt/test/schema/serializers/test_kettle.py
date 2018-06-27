import elt.schema.serializers.kettle as kettle


def test_config():
    schema = kettle.loads("sfdc", SAMPLE_KETTLE_CONFIG)

    import pdb; pdb.set_trace()

    assert(("User", "Id") in schema.columns)
    assert(("User", "LastName") in schema.columns)


SAMPLE_KETTLE_CONFIG = """<?xml version="1.0" encoding="UTF-8"?>
<transformation>
  <step>
    <name>Insert / Update</name>
    <type>InsertUpdate</type>
  </step>
  <step>
    <name>Salesforce Input</name>
    <type>SalesforceInput</type>
    <module>User</module>
    <fields>
      <field>
        <name>User ID</name>
        <field>Id</field>
        <idlookup>Y</idlookup>
        <type>String</type>
        <format />
      </field>
      <field>
        <name>Username</name>
        <field>Username</field>
        <idlookup>Y</idlookup>
        <type>String</type>
        <format />
      </field>
      <field>
        <name>Last Name</name>
        <field>LastName</field>
        <idlookup>N</idlookup>
        <type>String</type>
        <format />
      </field>
      <field>
        <name>First Name</name>
        <field>FirstName</field>
        <idlookup>N</idlookup>
        <type>String</type>
        <format />
      </field>
      <field>
        <name>Suffix</name>
        <field>Suffix</field>
        <idlookup>N</idlookup>
        <type>String</type>
        <format />
      </field>
      <field>
        <name></name>
        <field>Name</field>
        <idlookup>N</idlookup>
        <type>String</type>
        <format />
      </field>
      <field>
        <name>Marketo Sales Insight Welcome Counter</name>
        <field>mkto_si__Sales_Insight_Counter__c</field>
        <idlookup>N</idlookup>
        <type>Number</type>
        <format />
      </field>
      <field>
        <name>Has Profile Photo</name>
        <field>IsProfilePhotoActive</field>
        <idlookup>N</idlookup>
        <type>Boolean</type>
        <format />
      </field>
      <field>
        <name>Start Date</name>
        <field>Start_Date__c</field>
        <idlookup>N</idlookup>
        <type>Date</type>
        <format>yyyy-MM-dd</format>
      </field>
      <field>
        <name>Last Login</name>
        <field>LastLoginDate</field>
        <idlookup>N</idlookup>
        <type>Date</type>
        <format>yyyy-MM-dd'T'HH:mm:ss'.000'XXX</format>
      </field>
    </fields>
  </step>
</transformation>
"""
