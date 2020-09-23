insert into users (
        username,
        email,
        salt,
        password,
        created_at,
        first_name,
        last_name,
        active,
        is_admin,
        api_token
    )
VALUES (
        'test',
        'test@email.com',
        '2PtW4JdyFwPrNkQH3vvzXtLWMHAx8zXI1yBqJQBaYbFPH7lU5aEaWFV0pS4Ir2XWq24Cs1Rf2Xm9hmm5',
        '$argon2id$v=19$m=512,t=4,p=2$uvc+J4RQylkLwTiHkHJubQ$E4YWUUgWj2hwMTMinNohVQ',
        '2020-09-23 09:29:05.922718',
        'test',
        'test',
        true,
        true,
        'testing_api_token'
    );