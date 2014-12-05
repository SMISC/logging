<?php

class Bot extends Eloquent
{
    protected $table = 'team_bot';
    protected $connection = 'competition';

    public function team()
    {
        return $this->belongsTo('Team');
    }
}
