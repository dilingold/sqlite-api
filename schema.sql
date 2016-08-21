drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  subName text not null,
  groupId text not null,
  sensorId text not null
);