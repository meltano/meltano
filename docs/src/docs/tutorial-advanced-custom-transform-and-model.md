# Custom Transforms and Models

This tutorial explains how to add custom data transformations and Meltano models.

## Prerequisites

You have successfully extracted and loaded data from your Salesforce account by following the steps described in the Salesforce Tutorial.

## Context and Examples

In this example, we would like to focus on closed opportunities only (i.e. actual sales) and allow grouping by year, quarter and the following categorical dimensions:

- size of the deal, defined by the following buckets: Small (<5k$), Medium (5k$ - 25k$), Big (25k$ - 100k$), Jumbo (>100k$)
- type of deal, i.e. "New Business" vs "Renewal" vs "Add-On Business"
- client's location
- client's industry
- client's size, defined by the following buckets: Small (<100 employees), Medium (100 - 999 employees), Large (1k - 20k employees), Strategic (>20k employees)

Please see example table outputs below.

Size and number of won opportunities by country and company size. 

```
  company_country   |      company_size      | total_contract_value | average_contract_value | total_contracts 
--------------------+------------------------+----------------------+------------------------+-----------------
 France             | 1 - Small (<100)       |              1008.00 |                 504.00 |               2
 France             | 2 - Medium (100 - 999) |                48.00 |                  48.00 |               1
 France             | 3 - Large (1k - 20k)   |               480.00 |                 480.00 |               1
 France             | 5 - Unknown            |              1344.00 |                 336.00 |               4
 Germany            | 1 - Small (<100)       |              1601.49 |                 320.30 |               5
 Germany            | 2 - Medium (100 - 999) |               144.00 |                 144.00 |               1
 Germany            | 3 - Large (1k - 20k)   |             46473.86 |               46473.86 |               1
 Germany            | 5 - Unknown            |              4329.64 |                 721.61 |               6
 United States      | 1 - Small (<100)       |              2904.33 |                 484.06 |               6
 United States      | 2 - Medium (100 - 999) |               192.00 |                 192.00 |               1
 United States      | 3 - Large (1k - 20k)   |             92703.00 |               46351.50 |               2
 United States      | 5 - Unknown            |               384.00 |                  96.00 |               4
```

Number of won opportunities by quarter, year and industry segment:

```
 closed_quarter | closed_year |               industry                | total_contracts 
----------------+-------------+---------------------------------------+-----------------
              4 |        2018 | Financial Services                    |               1
              4 |        2018 | Integrated Telecommunication Services |               2
              4 |        2018 | Internet                              |               1
              4 |        2018 | Internet Software & Services          |               7
              4 |        2018 | Retailing                             |               1
              4 |        2018 | Specialized Consumer Services         |               3
              4 |        2018 | Telecom / Communication Services      |               8
              4 |        2018 | Professional Services                 |               1
              1 |        2019 | Biotechnology                         |               1
              1 |        2019 | Consumer Discretionary                |               1
              1 |        2019 | Financial Services                    |               1
              1 |        2019 | Government                            |               1
              1 |        2019 | Internet Software & Services          |               3
              1 |        2019 | Specialized Consumer Services         |              13
              1 |        2019 | Technology                            |               2
```

Number of won opportunities by quarter, year, deal type, deal size and company size:

```
 closed_quarter | closed_year | opportunity_type |       deal_size       |      company_size      | total_contracts 
----------------+-------------+------------------+-----------------------+------------------------+-----------------
              1 |        2018 | Add-On Business  | 1 - Small (<5k)       | 5 - Unknown            |               1
              1 |        2018 | New Business     | 1 - Small (<5k)       | 1 - Small (<100)       |              11
              1 |        2018 | New Business     | 1 - Small (<5k)       | 2 - Medium (100 - 999) |               1
              1 |        2018 | New Business     | 1 - Small (<5k)       | 3 - Large (1k - 20k)   |               1
              1 |        2018 | New Business     | 1 - Small (<5k)       | 5 - Unknown            |              11
              1 |        2019 | Add-On Business  | 1 - Small (<5k)       | 1 - Small (<100)       |               1
              1 |        2019 | Add-On Business  | 1 - Small (<5k)       | 2 - Medium (100 - 999) |               1
              1 |        2019 | Add-On Business  | 1 - Small (<5k)       | 5 - Unknown            |               3
              1 |        2019 | Add-On Business  | 3 - Big (25k - 100k)  | 3 - Large (1k - 20k)   |               1
              1 |        2019 | New Business     | 1 - Small (<5k)       | 1 - Small (<100)       |               1
              1 |        2019 | New Business     | 1 - Small (<5k)       | 2 - Medium (100 - 999) |               2
              1 |        2019 | New Business     | 1 - Small (<5k)       | 5 - Unknown            |              10
              1 |        2019 | New Business     | 2 - Medium (5k - 25k) | 1 - Small (<100)       |               1
              1 |        2019 | Renewal          | 1 - Small (<5k)       | 1 - Small (<100)       |               3
              1 |        2019 | Renewal          | 1 - Small (<5k)       | 3 - Large (1k - 20k)   |               1
              1 |        2019 | Renewal          | 1 - Small (<5k)       | 5 - Unknown            |               1
              1 |        2019 | Renewal          | 3 - Big (25k - 100k)  | 3 - Large (1k - 20k)   |               1
              2 |        2018 | Add-On Business  | 1 - Small (<5k)       | 1 - Small (<100)       |               1
              4 |        2017 | New Business     | 1 - Small (<5k)       | 5 - Unknown            |               1
```

## Adding Custom Transforms

Transforms in Meltano are implemented by using [dbt](https://www.getdbt.com/). All Meltano generated projects have a `transform/` directory, which is populated with the required configuration, models, packages, etc in order to run the transformations (i.e. `sfdc-project/transform`). When `meltano elt tap-salesforce target-postgres --transform run` is executed, both default and custom dbt transformations in the `transform/` directory are being performed. 

If you are not familiar with dbt, please visit [dbt's documentation](https://docs.getdbt.com/). You can also check the section in Meltano's documentation on [Transforms](https://www.meltano.com/docs/meltano-cli.html#transforms) for more details.

Let's generate two additional transformations, which will produce:

- A table that includes won opportunities only and a custom category column for deal_size.
- A table that includes account categories, clients' countries, industries and a custom category column for company_size. 

These tables must be added as `dbt models`, i.e. `.sql` files under the `sfdc-project/transform/models/my_meltano_project/` directory or any of its subdirectories. This will allow Meltano to discover the new transformations and execute. 

In this case, we'll create a new `sfdc/transform` subdirectory and save the sql files there.

```bash
cd sfdc-project/transform/models/my_meltano_project/
mkdir sfdc
cd sfdc
mkdir transform
cd transform
```

`sfdc-project/transform/models/my_meltano_project/sfdc/transform/opportunity_won.sql`:

```
with source as (
    
    -- Use the base sf_opportunity model defined by Meltano's 
    --  prepackaged tap_salesforce model
    select * from {{ref('sf_opportunity')}}

),

opportunity_won as (
    select
        -- Attributes directly fetched from the Opportunity Table
        opportunity_id,
        account_id,
        owner_id,

        opportunity_type,
        lead_source,

        amount,

        -- Additional Calculated Fields

        -- Add a deal size categorical dimension
        CASE WHEN
          amount :: DECIMAL < 5000
          THEN '1 - Small (<5k)'
        WHEN amount :: DECIMAL >= 5000 AND amount :: DECIMAL < 25000
          THEN '2 - Medium (5k - 25k)'
        WHEN amount :: DECIMAL >= 25000 AND amount :: DECIMAL < 100000
          THEN '3 - Big (25k - 100k)'
        WHEN amount :: DECIMAL >= 100000
          THEN '4 - Jumbo (>100k)'
        ELSE '5 - Unknown'
        END                         AS deal_size,

        -- Add Closed Date, Month, Quarter and Year columns
        CAST(closed_date AS DATE) as closed_date, 
        EXTRACT(MONTH FROM closed_date) closed_month,
        EXTRACT(QUARTER FROM closed_date) closed_quarter, 
        EXTRACT(YEAR FROM closed_date) closed_year  

    from source

    where is_won = true and is_closed = true
)

select * from opportunity_won
```


`sfdc-project/transform/models/my_meltano_project/sfdc/transform/account_category.sql`:

```
with source as (
    
    -- Use the base sf_opportunity model defined by Meltano's 
    --  prepackaged tap_salesforce model
    select * from {{ref('sf_account')}}

),

account_category as (

    select

        account_id,

        -- Set NULL values to 'Unknown'
        COALESCE(company_country, 'Unknown') as company_country,

        -- Set NULL values to 'Unknown'
        COALESCE(industry, 'Unknown') as industry,
        
        -- Add a company size categorical dimension
        CASE WHEN
          number_of_employees < 100
          THEN '1 - Small (<100)'
        WHEN number_of_employees >= 100 AND number_of_employees < 1000
          THEN '2 - Medium (100 - 999)'
        WHEN number_of_employees >= 1000 AND number_of_employees < 20000
          THEN '3 - Large (1k - 20k)'
        WHEN number_of_employees >= 20000
          THEN '4 - Strategic (>20k)'
        ELSE '5 - Unknown'
        END                         AS company_size

    from source
)

select * from account_category
```

Before we execute the transformation, we need to update `my_meltano_project` in `dbt_project.yml` in order to have the results of the transformations materialized in the `analytics` schema. For more details on materialization options, please check dbt's documentation.

Update the `my_meltano_project: null` in `sfdc-project/transform/dbt_project.yml` to:

`sfdc-project/transform/dbt_project.yml` 
```
... ... ...

models:
  ... ... ...

  my_meltano_project:
    materialized: table

  ... ... ...

... ... ...
```

```bash
source .env
#Runs transformation step only from the ELT step
meltano elt tap-salesforce target-postgres --transform only
```

## Adding Custom Models

In order to access the newly transformed data from the Analyze Section in Meltano UI, a `table.m5o` file, which defines the available columns and aggregates for each table should be created. A `model.m5o` file for representing how the tables are connected is also required. The files will be stored in the `model/` directory. For more details on how `.m5o` files are structured, please refer to [Meltano Models](https://www.meltano.com/docs/architecture.html#meltano-model) and [concepts related to Meltano Models](https://www.meltano.com/docs/concepts.html).

Account Category Table
`sfdc-project/model/account_category.table.m5o` 
```
{
  version = 1
  sql_table_name = account_category
  name = account_category
  columns {
    account_id {
      primary_key = true
      hidden = true
      type = string
      sql = "{{table}}.account_id"
    }
    company_country {
      label = Company Country
      description = Company Country
      type = string
      sql = "{{table}}.company_country"
    }
    company_size {
      label = Company Size
      description = Company Size
      type = string
      sql = "{{table}}.company_size"
    }
    industry {
      label = Industry
      description = Industry
      type = string
      sql = "{{table}}.industry"
    }
  }
}
```

Opportunities Won Table
`sfdc-project/model/opportunity_won.table.m5o` 
```
{
  version = 1
  sql_table_name = opportunity_won
  name = opportunity_won
  columns {
    opportunity_id {
      primary_key = true
      hidden = true
      type = string
      sql = "{{table}}.opportunity_id"
    }
    owner_id {
      label = Owner ID (User)
      hidden = yes
      type = string
      sql = "{{TABLE}}.owner_id"
    }
    account_id {
      label = Account ID
      hidden = yes
      type = string
      sql = "{{TABLE}}.account_id"
    }
    opportunity_type {
      label = Oportunity Type
      description = Oportunity Type
      type = string
      sql = "{{table}}.opportunity_type"
    }
    lead_source {
      label = Lead Source
      description = Lead Source
      type = string
      sql = "{{table}}.lead_source"
    }
    deal_size {
      label = Deal Size
      description = Deal Size
      type = string
      sql = "{{table}}.deal_size"
    }
    closed_date {
      label = Closed Date
      description = Date the Opportunity Closed
      type = string
      sql = "{{table}}.closed_date"
    }
    closed_month {
      label = Closed Month
      description = Month the Opportunity Closed
      type = string
      sql = "{{table}}.closed_month"
    }
    closed_quarter {
      label = Closed Quarter
      description = Quarter the Opportunity Closed
      type = string
      sql = "{{table}}.closed_quarter"
    }
    closed_year {
      label = Closed Year
      description = Year the Opportunity Closed
      type = string
      sql = "{{table}}.closed_year"
    }
  }
  aggregates {
    total_opportunities {
      label = Total Opportunities
      description = Total Opportunities
      type = count
      sql = "{{table}}.opportunity_id"
    }
    total_amount {
      label = Total Amount
      description = Total Amount
      type = sum
      sql = "{{table}}.amount"
    }
    avg_amount {
      label = Average Amount
      description = Average Amount
      type = avg
      sql = "{{table}}.amount"
    }
  }
}
```

Please note, the name this model will be `custom_sfdc` in order to differentiate it from the sfdc model that comes by default with Meltano:

`sfdc-project/model/custom_sfdc.model.m5o` 
```
{
  version = 1
  name = custom_sfdc
  connection = postgres_db
  label = Salesforce (Custom)
  designs {
    opportunity_won {
      label = Opportunities Won
      from = opportunity_won
      description = SFDC Opportunities Won
      joins {
        account_category {
          label = Opportunity
          sql_on = "opportunity_won.account_id = account_category.account_id"
          relationship = many_to_one
        }
      }
    }
  }
}
```

## Interact with Your Data in the Meltano UI

In order to start the Meltano UI, please go back into your terminal and run the following command:

```bash
# Start up the Meltano UI web application!
$ meltano ui
```

This will start a local web server at [http://localhost:5000](http://localhost:5000). 

As we have properly set the connection to our Postgres Database in the Salesforce Tutorial, we can now query and explore the extracted data:

- Navigate to `Analyze` > `CUSTOM SFDC` > `opportunity won`
- Toggle Columns and Aggregates buttons to generate the SQL query.
- Click the Run button to query the transformed tables in the `analytics` schema.
- Check the Results or Open the Charts accordion and explore the data!


## Closing Remarks

The same process for adding custom Transforms and Model(s) would be followed if we wanted to extract and analyze additional Salesforce Entities that were not fetched in the Salesforce Tutorial:

(1) Add the additional Entities to the list of Entities to be extracted when `meltano elt` runs.

As described in the Salesforce Tutorial, this can be done by using the meltano select command

```bash
meltano select tap-salesforce "Entity Name" "*"
```

You can find the names for the supported entities by running:

```bash
meltano select tap-salesforce --list --all
```

(2) Follow the steps above to add custom transformations and models for the new Entities.

(3) Run meltano elt to extract and transform the data.


```bash
meltano elt tap-salesforce target-postgres --transform run
```
