create or replace NONEDITIONABLE PROCEDURE  move_flood_detection_to_atp
AS
BEGIN
    insert into flood_detection@dblink_passport(row_id, current_level, precise_counter )
    select row_id, current_level, precise_counter
    from flood_detection;

    commit;

    execute immediate 'truncate table flood_detection';

END move_flood_detection_to_atp;