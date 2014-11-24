<?php

class Tweet extends Eloquent
{
    protected $table = 'tweet';

    public function entities()
    {
        return $this->hasMany('TweetEntity');
    }

    public function user()
    {
        return $this->belongsTo('TwitterUser');
    }
}
