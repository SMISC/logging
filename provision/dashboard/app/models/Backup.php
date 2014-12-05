<?php

class Backup extends Eloquent
{
    protected $table = 'backups';
    protected $connection = 'competition';

    public function scan()
    {
        return $this->hasOne('Scan');
    }
}
