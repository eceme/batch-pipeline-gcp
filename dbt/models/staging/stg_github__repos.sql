with source as (

    select * from {{ source('raw', 'github_repos') }}

),

renamed as (

    select
        -- ingestion metadata
        snapshot_date,
        ingested_at,
        category,

        -- identifiers
        cast(json_value(payload.id) as int64) as repo_id,
        json_value(payload.full_name) as full_name,
        json_value(payload.name) as repo_name,
        json_value(payload.owner.login) as owner_login,
        json_value(payload.owner.type) as owner_type,
        json_value(payload.html_url) as html_url,

        -- descriptive attributes
        json_value(payload.description) as description,
        json_value(payload.language) as language,
        json_value(payload.license.spdx_id) as license_spdx_id,
        json_value_array(payload.topics) as topics,
        json_value(payload.homepage) as homepage,
        cast(json_value(payload.archived) as bool) as is_archived,
        cast(json_value(payload.fork) as bool) as is_fork,
        timestamp(json_value(payload.created_at)) as created_at,
        timestamp(json_value(payload.pushed_at)) as pushed_at,

        -- daily metrics
        cast(json_value(payload.stargazers_count) as int64) as stars,
        cast(json_value(payload.forks_count) as int64) as forks,
        cast(json_value(payload.open_issues_count) as int64) as open_issues,
        -- watchers_count is a legacy alias of stargazers_count; subscribers_count is the real one.
        cast(json_value(payload.subscribers_count) as int64) as watchers,
        cast(json_value(payload.size) as int64) as size_kb

    from source

)

select * from renamed
