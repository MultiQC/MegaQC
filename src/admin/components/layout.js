import React from 'react';
import {AppBar, Layout} from 'react-admin';
import Typography from '@material-ui/core/Typography';
import {makeStyles} from '@material-ui/core/styles';
import Icon from '@material-ui/core/Icon';
import Link from '@material-ui/core/Link';

const useStyles = makeStyles({
    title: {
        flex: 1,
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
    },
    spacer: {
        flex: 1,
    },
    icon: {
        height: '1.2em'
    },
});

export function MegaQcAppBar(props) {
    const classes = useStyles();
    return (
        <AppBar {...props}>
            <Typography
                variant="h6"
                color="inherit"
                className={classes.title}
            >
                <Link href="/">
                    <Icon>
                        <img className={classes.icon} src="/static/img/favicon.svg"/>
                    </Icon>
                </Link>
                &nbsp;
                MegaQC - <span id="react-admin-title"/>
            </Typography>
            <span className={classes.spacer}/>
        </AppBar>
    );
};

export function MegaQcLayout(props) {
    return <Layout
        {...props}
        appBar={MegaQcAppBar}
    />;
}
