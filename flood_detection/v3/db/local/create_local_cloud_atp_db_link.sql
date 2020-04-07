--------------------------------------------------------
--  DDL for DB Link DBLINK_PASSPORT
--------------------------------------------------------

  CREATE DATABASE LINK "DBLINK_PASSPORT"
   CONNECT TO "SMARTPARKING" IDENTIFIED BY VALUES ':1'
   USING '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=asz8eqwfm8unca2_oowsgdemo_tpurgent.atp.oraclecloud.com))(security=(ssl_server_cert_dn="CN=adwc.uscom-east-1.oraclecloud.com,OU=Oracle BMCS US,O=Oracle Corporation,L=Redwood City,ST=California,C=US")))';
