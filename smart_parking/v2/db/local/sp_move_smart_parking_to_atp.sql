--------------------------------------------------------
--  DDL for Procedure MOVE_SMART_PARKING_TO_ATP
--------------------------------------------------------
set define off;

  CREATE OR REPLACE NONEDITIONABLE PROCEDURE "MOVE_SMART_PARKING_TO_ATP" 
AS
BEGIN
    insert into smart_parking@dblink_passport(row_id, carpark_id, created_date_time, total_slots, available_slots, carpark_status, 
                                            modified_date_time, precise_counter )
    select row_id, carpark_id, created_date_time, total_slots, available_slots, carpark_status, modified_date_time, precise_counter
    from smart_parking;

    commit;

    execute immediate 'truncate table smart_parking';

END move_smart_parking_to_atp;

/
