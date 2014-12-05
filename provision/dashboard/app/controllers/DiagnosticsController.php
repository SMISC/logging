<?php

class DiagnosticsController extends BaseController
{
    public function showOverview()
    {
        $this->layout->content = View::make('diagnostics.overview')->with(array(
        ));
    }
}
