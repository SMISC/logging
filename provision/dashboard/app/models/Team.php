<?php

class Team extends Eloquent
{
    protected $table = 'team';
    protected $connection = 'competition';

    public function bots()
    {
        return $this->hasMany('Bot');
    }
}
