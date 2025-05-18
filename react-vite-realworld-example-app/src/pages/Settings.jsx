import { Formik, Form, Field } from 'formik'
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from 'react-query'
import axios from 'axios'
import { useAuth, useUserQuery } from '../hooks'
import { FormErrors } from '../components'

function Settings() {
  const {
    data: { user },
  } = useUserQuery()
  // const {data} = useUserQuery()
  // const user = data?.user || {} // 确保 user 至少是一个空对象

  // if (!user) {
  //   return <div>Loading...</div>; // test codes;
  // }

  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { logout } = useAuth()

  async function onSubmit(values, { setErrors }) {
    try {
      const { data } = await axios.put(`/user`, { user: values })

      const updatedUsername = data?.user?.username

      logout(data?.user)

      queryClient.invalidateQueries(`/profiles/${updatedUsername}`)
      queryClient.invalidateQueries(`/user`)

      navigate(`/profile/${updatedUsername}`)
    } catch (error) {
      const { status, data } = error.response

      if (status === 422) {
        setErrors(data.errors)
      }
    }
  }

  // async function onSubmit(values, { setErrors }) {
  //   try {
  //     console.log("提交的数据:", values);  // ✅ 确保 values 正确
  //     const { data } = await axios.put(`/user`, { user: values }, {
  //       headers: { 'Content-Type': 'application/json' }
  //     });
  
  //     console.log("更新成功，后端返回:", data);
  
  //     const updatedUsername = data?.user?.username;
      
  //     if (updatedUsername) {
  //       queryClient.invalidateQueries(`/profiles/${updatedUsername}`);
  //     }
  //     queryClient.invalidateQueries(`/user`);
  
  //     navigate(`/profile/${updatedUsername}`);
  //   } catch (error) {
  //     console.error("更新失败", error.response);
  
  //     if (error.response?.status === 422) {
  //       setErrors(error.response.data.errors);
  //     }
  //   }
  // }
  

  return (
    <div className="settings-page">
      <div className="container page">
        <div className="row">
          <div className="col-md-6 offset-md-3 col-xs-12">
            <h1 className="text-xs-center">Your Settings</h1>
            <Formik onSubmit={onSubmit} initialValues={user} enableReinitialize>
              {({ isSubmitting }) => (
                <>
                  <FormErrors />
                  <Form>
                    <fieldset disabled={isSubmitting}>
                      <fieldset className="form-group">
                        <Field name="image" className="form-control" type="text" placeholder="URL of profile picture" />
                      </fieldset>
                      <fieldset className="form-group">
                        <Field
                          name="username"
                          className="form-control form-control-lg"
                          type="text"
                          placeholder="Your Name"
                        />
                      </fieldset>
                      <fieldset className="form-group">
                        <Field
                          as="textarea"
                          name="bio"
                          className="form-control form-control-lg"
                          rows={8}
                          placeholder="Short bio about you"
                        />
                      </fieldset>
                      <fieldset className="form-group">
                        <Field name="email" className="form-control form-control-lg" type="text" placeholder="Email" />
                      </fieldset>
                      <fieldset className="form-group">
                        <Field
                          name="password"
                          className="form-control form-control-lg"
                          type="password"
                          placeholder="Password"
                        />
                      </fieldset>
                      <button type="submit" className="btn btn-lg btn-primary pull-xs-right">
                        Update Settings
                      </button>
                    </fieldset>
                  </Form>
                </>
              )}
            </Formik>
            <hr />
            <button onClick={() => logout()} type="button" className="btn btn-outline-danger">
              Or click here to logout.
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
