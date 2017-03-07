drop table if exists posts;
create table posts (
	post_id integer primary key autoincrement,
	title text not null,
	post_body text not null,
	description text not null,
	date DATE DEFAULT (datetime('now','localtime')),
	author integer REFERENCES user(user_id)
);