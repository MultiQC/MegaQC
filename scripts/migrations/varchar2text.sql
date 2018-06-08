begin;
-- roles
alter table roles alter column name type text ;

-- users
alter table users alter column "username" type text ;
alter table users alter column "email" type text ;
alter table users alter column "salt" type text ;
alter table users alter column "password" type text ;
alter table users alter column "first_name" type text ;
alter table users alter column "last_name" type text ;
alter table users alter column "api_token" type text ;

-- report
alter table report alter column "report_hash" type text ;

-- report_meta
alter table report_meta alter column "report_meta_key" type text ;
alter table report_meta alter column "report_meta_value" type text ;

-- plot_config
alter table plot_config alter column "config_type" type text ;
alter table plot_config alter column "config_name" type text ;
alter table plot_config alter column "config_dataset" type text ;
alter table plot_config alter column "data" type text ;

-- plot_data
alter table plot_data alter column "data" type text ;

-- plot_category
alter table plot_category alter column "category_name" type text ;
alter table plot_category alter column "data" type text ;

-- plot_favourite
alter table plot_favourite alter column "title" type text ;
alter table plot_favourite alter column "description" type text ;
alter table plot_favourite alter column "plot_type" type text ;
alter table plot_favourite alter column "data" type text ;

-- dashboard
alter table dashboard alter column "title" type text ;
alter table dashboard alter column "data" type text ;

-- sample_data_type
alter table sample_data_type alter column "data_id" type text ;
alter table sample_data_type alter column "data_section" type text ;
alter table sample_data_type alter column "data_key" type text ;

-- sample_data
alter table sample_data alter column "value" type text ;

-- sample
alter table sample alter column "sample_name" type text ;

-- sample_filter
alter table sample_filter alter column "sample_filter_name" type text ;
alter table sample_filter alter column "sample_filter_tag" type text ;
alter table sample_filter alter column "sample_filter_data" type text ;

-- uploads
alter table uploads alter column "status" type text ;
alter table uploads alter column "path" type text ;
alter table uploads alter column "message" type text ;
commit ;
