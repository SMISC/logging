<?php

class TweetEntity extends Eloquent
{
    protected $table = 'tweet_entity';
    protected $connection = 'competition';

    public function entities()
    {
        return $this->hasMany('TweetEntity');
    }

    public function tweet()
    {
        return $this->belongsTo('Tweet');
    }
}
