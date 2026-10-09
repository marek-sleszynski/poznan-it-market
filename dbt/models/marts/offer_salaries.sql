{{ config(materialized='view') }}

select history.*
from {{ ref('offer_salary_history') }} as history
inner join {{ ref('latest_offers') }} as offers
    on offers.raw_offer_id = history.raw_offer_id
