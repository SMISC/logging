<?php

class UserTableSeeder extends Seeder
{
    public function run()
    {
        DB::table('users')->delete();

        User::create(array(
            'name' => 'Jacob Greenleaf',
            'username' => 'jacobgreenleaf',
            'password' => Hash::make('1234qwer')
        ));
    }
}
