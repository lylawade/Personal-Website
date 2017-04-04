drop table if exists posts;
create table posts (
	post_id integer primary key autoincrement,
	title text not null,
	post_body text not null,
	description text not null,
	date DATE DEFAULT (datetime('now','localtime')),
	author integer REFERENCES user(user_id)
);
drop table if exists users;
create table users (
	user_id integer primary key autoincrement,
	username text UNIQUE not null,
	password text not null
);