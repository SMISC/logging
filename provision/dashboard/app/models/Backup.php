<?php

class Backup extends Eloquent
{
    protected $table = 'backup';
    protected $connection = 'competition';

    public function scan()
    {
        return $this->hasOne('Scan');
    }
}
