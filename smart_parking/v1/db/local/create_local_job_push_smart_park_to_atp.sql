BEGIN
    DBMS_SCHEDULER.CREATE_JOB (
            job_name => '"GSMUSER".""',
            job_type => 'STORED_PROCEDURE',
            job_action => 'GSMUSER.MOVE_SMART_PARKING_TO_ATP',
            number_of_arguments => 0,
            start_date => TO_TIMESTAMP_TZ('2020-02-04 17:05:28.277000000 ASIA/SINGAPORE','YYYY-MM-DD HH24:MI:SS.FF TZR'),
            repeat_interval => 'FREQ=SECONDLY;INTERVAL=2;BYDAY=MON,TUE,WED,THU,FRI,SAT,SUN',
            end_date => NULL,
            enabled => FALSE,
            auto_drop => FALSE,
            comments => '');

    DBMS_SCHEDULER.SET_ATTRIBUTE( 
             name => '"GSMUSER".""', 
             attribute => 'logging_level', value => DBMS_SCHEDULER.LOGGING_OFF);
  
    DBMS_SCHEDULER.enable(
             name => '"GSMUSER".""');
END;